// Window-only capture. --read emits OCR text over stdout for local policy checks.
import AppKit
import ScreenCaptureKit
import Vision

enum ProbeError: Error { case denied, wrongApp, wrongWindow, focusChanged, invalidInput, markerMissing }

func recognize(_ image: CGImage) throws -> String {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    try VNImageRequestHandler(cgImage: image).perform([request])
    return (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}

func containsMarker(_ image: CGImage, _ marker: String) throws -> Bool {
    return try recognize(image).contains(marker)
}

@main struct WindowProbe {
    @MainActor static func foreground(_ title: String) throws -> CGWindowID {
        guard CGPreflightScreenCaptureAccess() else { throw ProbeError.denied }
        guard let app = NSWorkspace.shared.frontmostApplication,
              app.bundleIdentifier == "com.microsoft.VSCode" else { throw ProbeError.wrongApp }
        guard let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]],
              let front = windows.first(where: { ($0[kCGWindowLayer as String] as? Int) == 0 }),
              front[kCGWindowOwnerPID as String] as? pid_t == app.processIdentifier,
              front[kCGWindowName as String] as? String == title,
              let id = front[kCGWindowNumber as String] as? CGWindowID else { throw ProbeError.wrongWindow }
        return id
    }

    @MainActor static func main() async {
        do {
            let args = CommandLine.arguments
            if args.count == 2 && args[1] == "--permission-status" {
                print(CGPreflightScreenCaptureAccess() ? "authorized" : "permission-required")
                return
            }
            if args.count == 4 && args[1] == "--check" {
                guard let expected = CGWindowID(args[3]), try foreground(args[2]) == expected else {
                    throw ProbeError.focusChanged
                }
                print("{}")
                return
            }
            if args.count == 2 && args[1] == "--self-test" {
                let sample = NSImage(size: NSSize(width: 640, height: 90))
                sample.lockFocus()
                NSColor.white.setFill()
                NSBezierPath(rect: NSRect(origin: .zero, size: sample.size)).fill()
                ("violet dispatch" as NSString).draw(at: NSPoint(x: 24, y: 24),
                    withAttributes: [.font: NSFont.systemFont(ofSize: 34), .foregroundColor: NSColor.black])
                sample.unlockFocus()
                guard let image = sample.cgImage(forProposedRect: nil, context: nil, hints: nil),
                      try containsMarker(image, "violet dispatch"),
                      try !containsMarker(image, "absent marker") else { throw ProbeError.markerMissing }
                print("Synthetic OCR passed")
                return
            }
            guard args.count == 3, !args[1].isEmpty, !args[2].isEmpty else { throw ProbeError.invalidInput }
            let readText = args[1] == "--read"
            let (title, marker) = (readText ? args[2] : args[1], args[2])
            FileHandle.standardError.write(Data("Switch to the approved fictional VS Code window within five seconds.\n".utf8))
            try await Task.sleep(nanoseconds: 5_000_000_000)
            let id = try foreground(title)
            let content = try await SCShareableContent.excludingDesktopWindows(true, onScreenWindowsOnly: true)
            guard let window = content.windows.first(where: { $0.windowID == id && $0.title == title && $0.owningApplication?.bundleIdentifier == "com.microsoft.VSCode" }),
                  try foreground(title) == id else { throw ProbeError.focusChanged }
            let filter = SCContentFilter(desktopIndependentWindow: window)
            let config = SCStreamConfiguration()
            config.showsCursor = false
            config.width = min(3840, Int(window.frame.width * 2))
            config.height = min(2160, Int(window.frame.height * 2))
            let image = try await SCScreenshotManager.captureImage(contentFilter: filter, configuration: config)
            guard try foreground(title) == id else { throw ProbeError.focusChanged }
            let text = try recognize(image)
            guard try foreground(title) == id else { throw ProbeError.focusChanged }
            if readText {
                guard text.utf8.count <= 24000 else { throw ProbeError.invalidInput }
                let data = try JSONSerialization.data(withJSONObject: ["text": text, "window_id": id])
                print(String(decoding: data, as: UTF8.self))
            } else {
                guard text.contains(marker) else { throw ProbeError.markerMissing }
                print("Approved window: expected marker detected")
            }
        } catch {
            if let reason = error as? ProbeError {
                FileHandle.standardError.write(Data("Capture check failed: \(reason)\n".utf8))
            }
            FileHandle.standardError.write(Data("Probe stopped. Check permission, exact foreground title and fictional marker.\n".utf8))
            exit(1)
        }
    }
}
