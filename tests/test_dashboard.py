import os
import unittest
from datetime import date
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


with patch.dict(os.environ, {
    "ENV_MODE": "test",
    "DATABASE_URL": "postgresql://test:test@localhost/test",
    "SECRET_KEY": "test-key",
    **{f"R2_{name}": "test" for name in (
        "ACCESS_KEY", "SECRET_KEY", "ACCOUNT_ID", "BUCKET_NAME", "ENDPOINT", "PUBLIC_DOMAIN"
    )},
}):
    from auth import create_access_token
    from models import AppList, AppUser, DailyStat, DailyUserActivity, PayOrder, Product
    from routers.dashboard import get_db, report_day_bounds, router


class DashboardRoutesTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.addCleanup(self.engine.dispose)
        for model in (AppList, AppUser, DailyStat, DailyUserActivity, PayOrder, Product):
            model.__table__.create(self.engine)
        self.day = date(2026, 11, 23)
        self.start, _ = report_day_bounds(self.day)
        with Session(self.engine) as session:
            session.add_all([
                AppList(package_name="example.alpha", app_name="Alpha"),
                AppList(package_name="example.beta", app_name="Beta"),
                AppUser(user_id=1, package_name="example.alpha", country="US", created_time=self.start),
                AppUser(user_id=2, package_name="example.alpha", country="US",
                        created_time=self.start, is_anchor=True),
                DailyUserActivity(stat_date=self.day, user_id=1),
                DailyUserActivity(stat_date=self.day, user_id=2),
            ])
            session.commit()

        async def test_db():
            # Execute the real SQL on SQLite through the route's async interface.
            with Session(self.engine) as session:
                db = AsyncMock(spec=AsyncSession)
                db.execute.side_effect = session.execute
                db.scalars.side_effect = session.scalars
                db.scalar.side_effect = session.scalar
                yield db

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_db] = test_db
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.client.cookies.set("admin_token", create_access_token({"sub": "test-admin"}))

    def report(self, package="example.alpha", **filters):
        response = self.client.get("/admin/dashboard", params={
            "date": self.day.isoformat(), "package": package, **filters,
        })
        self.assertEqual(response.status_code, 200)
        return response.context["rows"][0]

    def test_price_fallback_matches_order_type_and_latest_product(self):
        with Session(self.engine) as session:
            session.add_all([
                Product(package_name="example.alpha", sku="shared", type=0, currency_price=1.99),
                Product(package_name="example.alpha", sku="shared", type=0, currency_price=4.99),
                Product(package_name="example.alpha", sku="shared", type=1, currency_price=8.99),
                Product(package_name="example.alpha", sku="shared", type=2, currency_price=19.99),
                Product(package_name="example.beta", sku="shared", type=0, currency_price=99.99),
            ])
            session.commit()

        for order_type, expected_income in ((0, 4.99), (1, 8.99), (2, 19.99)):
            with self.subTest(order_type=order_type):
                with Session(self.engine) as session:
                    session.execute(delete(PayOrder))
                    session.add(PayOrder(
                        user_id=1, package_name="example.alpha", sku="shared", type=order_type,
                        order_status=1, updated_time=self.start + 10,
                    ))
                    session.commit()
                row = self.report()
                self.assertEqual(row["new_income"], expected_income)
                self.assertEqual(row["total_income"], expected_income)
                self.assertEqual(row["income_per_payer"], expected_income)
                self.assertEqual(row["orders"], 1)
                self.assertEqual(row["missing_prices"], 0)

    def test_recorded_order_price_and_currency_take_precedence(self):
        with Session(self.engine) as session:
            session.add_all([
                Product(package_name="example.alpha", sku="shared", type=0,
                        currency_price=4.99, currency_code="EUR"),
                PayOrder(user_id=1, package_name="example.alpha", sku="shared", type=0,
                         order_status=1, updated_time=self.start + 10,
                         currency_price=7, currency_code="USD"),
            ])
            session.commit()
        row = self.report(currency="USD")
        self.assertEqual(row["new_income"], 7)
        self.assertEqual(row["total_income"], 7)
        self.assertEqual(row["missing_prices"], 0)

    def test_cross_package_orders_use_user_country_and_exclude_anchors(self):
        with Session(self.engine) as session:
            session.add_all([
                AppUser(user_id=3, package_name="example.alpha", country="JP",
                        created_time=self.start - 1),
                PayOrder(user_id=1, package_name="example.beta", order_status=1,
                         updated_time=self.start + 10, currency_price=7),
                PayOrder(user_id=2, package_name="example.beta", order_status=1,
                         updated_time=self.start + 10, currency_price=90),
                PayOrder(user_id=3, package_name="example.beta", order_status=1,
                         updated_time=self.start + 10, currency_price=11),
            ])
            session.commit()

        for country, expected_income, expected_payers, expected_new_income in (
            ("", 18, 2, 7), ("US", 7, 1, 7), ("JP", 11, 1, 0), ("CA", 0, 0, 0),
        ):
            with self.subTest(country=country):
                row = self.report(package="example.beta", country=country)
                self.assertEqual(row["total_income"], expected_income)
                self.assertEqual(row["new_income"], expected_new_income)
                self.assertEqual(row["total_payers"], expected_payers)
                self.assertEqual(row["orders"], expected_payers)
                self.assertEqual(row["dau"], expected_payers)
        self.assertEqual(self.report()["total_income"], 0)
