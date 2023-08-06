import unittest

from server import Chat, Comment


class TestChat(unittest.TestCase):
    def setUp(self):
        self.chat = Chat(max_messages=5, message_lifetime=3600, max_message_size=1024)

    def test_add_message(self):
        self.assertEqual(len(self.chat.messages), 0)
        self.chat.add_message("Message 1", "User 1")
        self.assertEqual(len(self.chat.messages), 1)

    def test_add_message_exceed_max_messages(self):
        for i in range(6):
            self.chat.add_message(f"Message {i}", f"User {i}")
        self.assertEqual(len(self.chat.messages), 6)

    def test_add_comment(self):
        self.chat.add_message("Message 1", "User 1")
        self.assertEqual(len(self.chat.messages), 1)  # Ensure message is added
        self.chat.add_comment(0, "Comment 1", "User 2")
        self.assertIsInstance(self.chat.messages[0]["comments"][0], Comment)

    def test_cleanup_messages(self):
        self.chat.add_message("Message 1", "User 1")
        self.chat.add_message("Message 2", "User 2")
        self.assertEqual(len(self.chat.messages), 2)
        self.chat.cleanup_messages()
        self.assertEqual(len(self.chat.messages), 2)
        # Simulate time passing more than the message_lifetime
        self.chat.messages[0]["timestamp"] = 0
        self.chat.cleanup_messages()
        self.assertEqual(len(self.chat.messages), 1)

    def test_is_user_banned(self):
        self.assertFalse(self.chat.is_user_banned("User 1"))
        self.chat.report_user("User 1")
        self.assertFalse(self.chat.is_user_banned("User 1"))
        self.chat.report_user("User 1")
        self.assertFalse(self.chat.is_user_banned("User 1"))
        self.chat.report_user("User 1")
        self.assertTrue(self.chat.is_user_banned("User 1"))

    def test_ban_user(self):
        self.assertFalse(self.chat.is_user_banned("User 1"))
        self.chat.ban_user("User 1")
        self.assertTrue(self.chat.is_user_banned("User 1"))

    def test_add_message_banned_user(self):
        self.chat.ban_user("User 1")
        self.chat.add_message("Message 1", "User 1")
        self.assertEqual(len(self.chat.messages), 0)

    def test_add_comment_banned_user(self):
        self.chat.add_message("Message 1", "User 1")
        self.chat.ban_user("User 2")
        self.chat.add_comment(0, "Comment 1", "User 2")
        self.assertEqual(len(self.chat.messages[0]["comments"]), 0)


if __name__ == '__main__':
    unittest.main()
