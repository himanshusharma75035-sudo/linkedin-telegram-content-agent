import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import delivery_worker
import enqueue_post


class QueueTests(unittest.TestCase):
    def test_enqueue_creates_independent_target_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            outbox = Path(temporary)
            with patch.object(enqueue_post, "OUTBOX_DIR", outbox):
                message_id = enqueue_post.enqueue("Finance post", ["telegram", "linkedin"])

            data = json.loads((outbox / f"{message_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(data["text"], "Finance post")
            self.assertFalse(data["targets"]["telegram"]["delivered"])
            self.assertFalse(data["targets"]["linkedin"]["delivered"])

    def test_partial_success_retries_only_failed_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outbox = root / "outbox"
            sent = root / "sent"
            failed = root / "failed"

            with patch.object(enqueue_post, "OUTBOX_DIR", outbox):
                message_id = enqueue_post.enqueue("Post", ["telegram", "linkedin"])
            path = outbox / f"{message_id}.json"

            with (
                patch.object(delivery_worker, "SENT_DIR", sent),
                patch.object(delivery_worker, "FAILED_DIR", failed),
                patch.object(delivery_worker, "send_message", return_value={"result": {"message_id": 7}}),
                patch.object(
                    delivery_worker,
                    "publish_post",
                    side_effect=RuntimeError("temporary LinkedIn failure"),
                ),
            ):
                complete = delivery_worker.process_message(path)

            self.assertFalse(complete)
            pending = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(pending["targets"]["telegram"]["delivered"])
            self.assertFalse(pending["targets"]["linkedin"]["delivered"])

            with (
                patch.object(delivery_worker, "SENT_DIR", sent),
                patch.object(delivery_worker, "FAILED_DIR", failed),
                patch.object(delivery_worker, "send_message") as telegram_mock,
                patch.object(
                    delivery_worker,
                    "publish_post",
                    return_value={"post_id": "urn:li:share:123", "image_urn": None},
                ),
            ):
                complete = delivery_worker.process_message(path)

            self.assertTrue(complete)
            telegram_mock.assert_not_called()
            archived = json.loads((sent / path.name).read_text(encoding="utf-8"))
            self.assertEqual(
                archived["targets"]["linkedin"]["reference"],
                "https://www.linkedin.com/feed/update/urn:li:share:123/",
            )

    def test_enqueue_can_store_linkedin_image_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            outbox = Path(temporary)
            with patch.object(enqueue_post, "OUTBOX_DIR", outbox):
                message_id = enqueue_post.enqueue(
                    "Finance post",
                    ["telegram", "linkedin"],
                    image_path="C:\\images\\finance.png",
                    image_alt_text="Finance visual",
                )

            data = json.loads((outbox / f"{message_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(data["image_path"], "C:\\images\\finance.png")
            self.assertEqual(data["image_alt_text"], "Finance visual")

    def test_clean_post_text_normalizes_smart_punctuation_damage(self):
        raw = 'Audit???not checklist. Hugging Face???s test proposed an ???AI Kill Switch Act???.'
        cleaned = enqueue_post.clean_post_text(raw)
        self.assertEqual(
            cleaned,
            'Audit - not checklist. Hugging Face\'s test proposed an "AI Kill Switch Act".',
        )


if __name__ == "__main__":
    unittest.main()
