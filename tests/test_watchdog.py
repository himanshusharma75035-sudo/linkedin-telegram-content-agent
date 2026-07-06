import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import post_watchdog


class WatchdogTests(unittest.TestCase):
    def test_not_due_before_check_time(self):
        monday = datetime(2026, 7, 6, 12, 34)
        self.assertEqual(post_watchdog.check(monday), "not_due")

    def test_missing_post_sends_one_alert(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch.object(post_watchdog, "SENT_DIR", root / "sent"),
                patch.object(post_watchdog, "OUTBOX_DIR", root / "outbox"),
                patch.object(post_watchdog, "STATE_FILE", root / "state.json"),
                patch.object(post_watchdog, "send_message") as send_mock,
            ):
                monday = datetime(2026, 7, 6, 12, 35)
                self.assertEqual(post_watchdog.check(monday), "missing")
                self.assertEqual(post_watchdog.check(monday), "already_alerted")
                send_mock.assert_called_once()

    def test_confirmed_post_does_not_alert(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sent = root / "sent"
            sent.mkdir()
            (sent / "20260706-example.json").write_text("{}\n", encoding="utf-8")
            with (
                patch.object(post_watchdog, "SENT_DIR", sent),
                patch.object(post_watchdog, "OUTBOX_DIR", root / "outbox"),
                patch.object(post_watchdog, "STATE_FILE", root / "state.json"),
                patch.object(post_watchdog, "send_message") as send_mock,
            ):
                monday = datetime(2026, 7, 6, 12, 35)
                self.assertEqual(post_watchdog.check(monday), "confirmed")
                send_mock.assert_not_called()

    def test_token_expiry_warning_is_sent_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            token_file = root / "linkedin_token.json"
            now = datetime(2026, 7, 6, tzinfo=timezone.utc)
            expires_at = int((now + timedelta(days=6)).timestamp())
            token_file.write_text(
                f'{{"expires_at": {expires_at}}}\n',
                encoding="utf-8",
            )
            with (
                patch.object(post_watchdog, "TOKEN_FILE", token_file),
                patch.object(post_watchdog, "STATE_FILE", root / "state.json"),
                patch.object(post_watchdog, "send_message") as send_mock,
            ):
                self.assertEqual(
                    post_watchdog.check_token_expiry(now),
                    "seven_day_warning",
                )
                self.assertEqual(
                    post_watchdog.check_token_expiry(now),
                    "already_alerted",
                )
                send_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
