import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import unittest
from pathlib import Path
from src.repository.auth import Hash


class TestHash(unittest.TestCase):

    def setUp(self):
        self.hash_instance = Hash()

    def test_verify_password_correct(self):
        plain_password = "test_password"
        hashed_password = self.hash_instance.pwd_context.hash(plain_password)

        result = self.hash_instance.verify_password(plain_password, hashed_password)

        self.assertTrue(result)

    def test_verify_password_incorrect(self):
        plain_password = "test_password"
        incorrect_password = "incorrect_password"
        hashed_password = self.hash_instance.pwd_context.hash(plain_password)

        result = self.hash_instance.verify_password(incorrect_password, hashed_password)

        self.assertFalse(result)

    def test_get_password_hash(self):
        password = "test_password"

        hashed_password = self.hash_instance.get_password_hash(password)

        self.assertTrue(self.hash_instance.verify_password(password, hashed_password))

if __name__ == '__main__':
    unittest.main()
    