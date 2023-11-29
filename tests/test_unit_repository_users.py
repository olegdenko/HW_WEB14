import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import sys
from pathlib import Path
import unittest
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_avatar,
    update_token,
    confirmed_email,
)
from src.database.models import User
from src.schemas import UserModel
from sqlalchemy.orm import Session

class TestUsers(unittest.TestCase):

    def setUp(self):
        self.db = Session()

    def tearDown(self):
        self.db.close()

    async def test_get_user_by_email_found(self):
        email = "test@example.com"
        user_data = {
            "username": "test_user",
            "email": email,
            "password": "test_password",
        }
        user_model = UserModel(**user_data)
        user = await create_user(user_model, self.db)

        result = await get_user_by_email(email, self.db)

        self.assertIsNotNone(result)
        self.assertEqual(result.email, email)

    async def test_get_user_by_email_not_found(self):
        email = "nonexistent@example.com"

        result = await get_user_by_email(email, self.db)

        self.assertIsNone(result)

    async def test_create_user(self):
        user_data = {
            "username": "new_user",
            "email": "new_user@example.com",
            "password": "new_password",
        }
        user_model = UserModel(**user_data)

        result = await create_user(user_model, self.db)

        self.assertIsNotNone(result)
        self.assertEqual(result.username, user_data["username"])
        self.assertEqual(result.email, user_data["email"])

    async def test_update_avatar(self):
        email = "test@example.com"
        user_data = {
            "username": "test_user",
            "email": email,
            "password": "test_password",
        }
        user_model = UserModel(**user_data)
        user = await create_user(user_model, self.db)
        new_avatar_url = "https://example.com/new_avatar.jpg"

        # Act
        result = await update_avatar(email, new_avatar_url, self.db)

        self.assertIsNotNone(result)
        self.assertEqual(result.avatar, new_avatar_url)

    async def test_update_token(self):
        email = "test@example.com"
        user_data = {
            "username": "test_user",
            "email": email,
            "password": "test_password",
        }
        user_model = UserModel(**user_data)
        user = await create_user(user_model, self.db)
        new_refresh_token = "new_refresh_token"

        await update_token(user, new_refresh_token, self.db)
        result = await get_user_by_email(email, self.db)

        self.assertIsNotNone(result)
        self.assertEqual(result.refresh_token, new_refresh_token)

    async def test_confirmed_email(self):
        email = "test@example.com"
        user_data = {
            "username": "test_user",
            "email": email,
            "password": "test_password",
        }
        user_model = UserModel(**user_data)
        user = await create_user(user_model, self.db)

        # Act
        await confirmed_email(email, self.db)
        result = await get_user_by_email(email, self.db)

        # Assert
        self.assertIsNotNone(result)
        self.assertTrue(result.confirmed)

if __name__ == '__main__':
    unittest.main()
