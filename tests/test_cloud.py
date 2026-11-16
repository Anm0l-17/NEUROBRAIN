import io
import os
import unittest
from contextlib import redirect_stdout
from typing import ClassVar
from unittest.mock import patch

from neurobrain import cloud


class CloudImportTests(unittest.TestCase):
    def test_connection_reset_during_read_is_controlled(self):
        with patch.object(cloud, "build_opener") as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.read.side_effect = ConnectionResetError("peer reset")
            with self.assertRaisesRegex(cloud.MemoryError, "Cloud service unreachable"):
                cloud.request("https://example.invalid", "fictional")

    meta: ClassVar[dict] = dict(
        id="file",
        name="demo.md",
        parents=["folder"],
        trashed=False,
        mimeType="text/markdown",
        size="12",
        version="3",
    )

    def run_import(self, replies):
        settings = dict(
            NEUROBRAIN_DRIVE_FOLDER="folder",
            NEUROBRAIN_DRIVE_TOKEN="drive",
            SUPABASE_URL="https://demo.supabase.co",
            SUPABASE_PUBLISHABLE_KEY="key",
            NEUROBRAIN_USER_TOKEN="user",
        )
        with (
            patch.dict(os.environ, settings),
            patch.object(cloud, "request", side_effect=replies) as req,
            redirect_stdout(io.StringIO()),
        ):
            code = cloud.main(["import", "file"])
        return code, req.call_args_list

    def test_import_posts_policy_checked_chunks(self):
        code, calls = self.run_import(
            [self.meta, b"violet\namber", self.meta, {"version": 1}]
        )
        self.assertEqual(code, 0)
        self.assertEqual(
            calls[-1].kwargs["payload"]["pieces"], [("violet\namber", 0, 12, 1, 2)]
        )
        self.assertEqual(
            calls[-1].args, ("https://demo.supabase.co/rest/v1/rpc/c2_memory", "user")
        )

    def test_refusal_precedes_cloud_storage(self):
        for replies in (
            [dict(self.meta, parents=["other"])],
            [dict(self.meta, name="../demo.md")],
            [self.meta, b"neurobrain: do-not-store"],
            [self.meta, b"password: demo"],
            [self.meta, b"ok", dict(self.meta, version="4")],
        ):
            with self.subTest(replies=replies):
                code, calls = self.run_import(replies)
                self.assertEqual(code, 1)
                self.assertTrue(all("googleapis.com" in c.args[0] for c in calls))
