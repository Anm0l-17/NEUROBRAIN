# Ralph for NeuroBrain

Run commands from this repository. `./ralph.sh --print-name` derives the sandbox name from the agent and repository path. Use `./ralph.sh --login` to create or attach to that sandbox. During cleanup, remove only that exact sandbox name; never remove sandboxes for other projects.

Before starting the loop, define an approved PRD in `.agent/prd/PRD.md`, its summary in `.agent/prd/SUMMARY.md`, and tasks in `.agent/tasks.json` with corresponding task specifications. The current task list is intentionally empty.

CodeRabbit is installed and authenticated on the host. Run `coderabbit review --agent -t uncommitted` here when a review of local changes is wanted.
