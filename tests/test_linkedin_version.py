import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import linkedin_post


class LinkedInVersionTests(unittest.TestCase):
    def test_default_version_is_pinned(self):
        with (
            tempfile.TemporaryDirectory() as temporary,
            patch.object(linkedin_post, "ENV_FILE", Path(temporary) / "missing.env"),
            patch.dict(os.environ, {}, clear=True),
        ):
            self.assertEqual(
                linkedin_post.linkedin_version(),
                linkedin_post.DEFAULT_LINKEDIN_VERSION,
            )

    def test_env_file_can_override_version(self):
        with tempfile.TemporaryDirectory() as temporary:
            env_file = Path(temporary) / "linkedin.env"
            env_file.write_text("LINKEDIN_API_VERSION=202605\n", encoding="utf-8")
            with (
                patch.object(linkedin_post, "ENV_FILE", env_file),
                patch.dict(os.environ, {}, clear=True),
            ):
                self.assertEqual(linkedin_post.linkedin_version(), "202605")


if __name__ == "__main__":
    unittest.main()
