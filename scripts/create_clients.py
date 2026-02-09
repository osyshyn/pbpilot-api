import asyncio
import random
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config.database import async_session_maker
from models.client import Client


FIRST_NAMES = [
    "John", "Michael", "David", "Chris", "Daniel",
    "James", "Robert", "Mark", "Paul", "Andrew",
]

LAST_NAMES = [
    "Smith", "Johnson", "Brown", "Taylor", "Anderson",
    "Thomas", "Jackson", "White", "Harris", "Martin",
]

STREETS = [
    "Main Street", "Oak Avenue", "Sunset Blvd",
    "Maple Drive", "Cedar Road", "Pine Lane",
]


async def create_client(
    name: str,
    surname: str,
    email: str,
    phone_number: str,
    business_address: str,
) -> bool:
    async with async_session_maker() as session:
        result = await session.execute(select(Client).where(Client.email == email))
        existing_client = result.scalar_one_or_none()

        if existing_client:
            print(f"❌ Client with email '{email}' already exists")
            return False

        try:
            client = Client(
                name=name,
                surname=surname,
                email=email,
                phone_number=phone_number,
                business_address=business_address,
            )
            session.add(client)
            await session.commit()
            print(f"✅ Client '{email}' created")
            return True

        except IntegrityError as e:
            await session.rollback()
            print(f"❌ Integrity error: {e}")
            return False

        except Exception as e:
            await session.rollback()
            print(f"❌ Unexpected error: {e}")
            return False


async def main() -> None:
    password_seed = random.randint(1000, 9999)

    for i in range(50):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"
        phone = f"+1555{random.randint(1000000, 9999999)}"
        address = f"{random.randint(1, 999)} {random.choice(STREETS)}"

        await create_client(
            name=first_name,
            surname=last_name,
            email=email,
            phone_number=phone,
            business_address=address,
        )

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
