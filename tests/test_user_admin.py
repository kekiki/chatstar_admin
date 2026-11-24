import os
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession


# The routes use a fake session, so the tests don't need a configured database.
with patch.dict(os.environ, {
    "ENV_MODE": "test",
    "DATABASE_URL": "postgresql://test:test@localhost/test",
    "SECRET_KEY": "test-key",
    **{f"R2_{name}": "test" for name in (
        "ACCESS_KEY", "SECRET_KEY", "ACCOUNT_ID", "BUCKET_NAME", "ENDPOINT", "PUBLIC_DOMAIN"
    )},
}):
    from auth import create_access_token
    from models import AppUser, BlackWhiteUser
    from routers.user import get_db, router


class AdminUserRoutesTest(unittest.TestCase):
    def setUp(self):
        self.user = AppUser(
            user_id=123, avatar="https://example.com/avatar.jpg", nickname="Example", country="US"
        )
        self.db = AsyncMock(spec=AsyncSession)
        self.db.execute.return_value = Mock()
        self.db.execute.return_value.scalar_one_or_none.side_effect = [self.user, None]

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = lambda: self.db

        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.client.cookies.set("admin_token", create_access_token({"sub": "test-admin"}))

    def test_setting_review_status_preserves_unsent_profile_fields(self):
        response = self.client.put("/admin/api/update_user", json={
            "user_id": self.user.user_id, "account_status": "0"
        })

        self.assertEqual(response.json()["code"], 200)
        self.assertEqual(self.user.avatar, "https://example.com/avatar.jpg")
        self.assertEqual(self.user.nickname, "Example")
        self.assertEqual(self.user.country, "US")
        entry = self.db.add.call_args.args[0]
        self.assertIsInstance(entry, BlackWhiteUser)
        self.assertEqual((entry.user_id, entry.status), (self.user.user_id, 0))
        self.db.commit.assert_awaited_once()

    def test_explicit_profile_updates_still_work(self):
        response = self.client.put("/admin/api/update_user", json={
            "user_id": self.user.user_id, "avatar": "", "nickname": "New nickname", "country": "CA"
        })

        self.assertEqual(response.json()["code"], 200)
        self.assertEqual((self.user.avatar, self.user.nickname, self.user.country), ("", "New nickname", "CA"))

    def test_user_list_shows_login_methods_without_exposing_credentials(self):
        for fields, expected in (
            ({"device_id": "device-1"}, {"游客登录"}),
            ({"google_id": "google-account-id", "device_id": "device-1"}, {"Google 登录"}),
            ({"device_id": "device-1", "password": "private-hash"}, {"游客登录", "密码登录"}),
            ({"google_id": "google-account-id", "password": "private-hash"}, {"Google 登录", "密码登录"}),
            ({}, {"未记录"}),
        ):
            with self.subTest(expected=expected):
                users_result = Mock()
                users_result.scalars.return_value.all.return_value = [AppUser(user_id=123, **fields)]
                empty_result = Mock()
                empty_result.scalars.return_value.all.return_value = []
                count_result = Mock()
                count_result.scalar_one.return_value = 1
                self.db.execute.side_effect = [empty_result, count_result, users_result] + [empty_result] * 2

                response = self.client.get("/admin/user")

                self.assertEqual(response.status_code, 200)
                self.assertIn(">登录方式</th>", response.text)
                cell = response.text.split('<td class="login-methods">', 1)[1].split("</td>", 1)[0]
                labels = {label for label in ("游客登录", "Google 登录", "密码登录", "未记录") if label in cell}
                self.assertEqual(labels, expected)
                self.assertNotIn("private-hash", response.text)
                self.assertNotIn("google-account-id", response.text)

    def test_changed_password_is_accepted_by_app_api_hash_config(self):
        # Keep this in sync with chatstar_api/app/security/jwt.py.
        app_passwords = CryptContext(schemes=["pbkdf2_sha256", "bcrypt", "sha256_crypt"], deprecated="auto")
        self.user.password = app_passwords.hash("old password")
        new_password = "新密码 Test!"

        response = self.client.put("/admin/api/change_password", json={
            "user_id": self.user.user_id, "new_password": new_password
        })

        self.assertEqual(response.json()["code"], 200)
        self.assertEqual(app_passwords.identify(self.user.password), "pbkdf2_sha256")
        self.assertTrue(app_passwords.verify(new_password, self.user.password))
        self.assertFalse(app_passwords.verify("old password", self.user.password))
        self.db.commit.assert_awaited_once()

    def test_empty_password_is_rejected(self):
        response = self.client.put("/admin/api/change_password", json={
            "user_id": self.user.user_id, "new_password": ""
        })

        self.assertEqual(response.status_code, 422)
        self.db.commit.assert_not_awaited()
