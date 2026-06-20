"""Create a demo user so the extension/dashboard have something to talk to."""
import asyncio
import uuid

from app.db.session import SessionLocal
from app.models.orm import ConnectedAccount, User, UserValue
from app.services.crypto import encrypt_token

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEMO_TOKEN = encrypt_token("demo-oauth-token-not-real")


async def main() -> None:
    async with SessionLocal() as session:
        existing = await session.get(User, DEMO_USER_ID)
        if existing:
            print(f"demo user already exists ({DEMO_USER_ID})")
            return

        user = User(id=DEMO_USER_ID, email="demo@dialecta.local", display_name="Demo User")
        session.add(user)
        session.add(ConnectedAccount(user_id=DEMO_USER_ID, provider="google_calendar", scope="readonly", encrypted_token=DEMO_TOKEN))
        session.add(ConnectedAccount(user_id=DEMO_USER_ID, provider="gmail", scope="readonly", encrypted_token=DEMO_TOKEN))
        session.add(UserValue(user_id=DEMO_USER_ID, statement="Saving for a trip in 8 weeks — no impulse buys over ₹2000", priority=10))
        session.add(UserValue(user_id=DEMO_USER_ID, statement="Be direct but kind in work emails", priority=5))
        await session.commit()
        print(f"created demo user {DEMO_USER_ID}")


if __name__ == "__main__":
    asyncio.run(main())
