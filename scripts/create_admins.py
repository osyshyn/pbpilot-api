import asyncio
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.pricing_plan import UserPlanEnum, BillingPeriodEnum

from config.database import async_session_maker
from models.user import User, UserRoleEnum
from services.jwt.hasher import Hasher


async def create_user(email: str, password: str, role: UserRoleEnum,free_reports_count:int) -> bool:  # noqa: D103
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            print(f"❌ Error: User with email '{email}' already exists")
            return False
        try:
            user = User(
                email=email,
                password=Hasher.hash_password(password),
                name='admin',
                surname='admin_user',
                role=role,
                phone_number='+1123456789',
                current_plan=UserPlanEnum.SOLO_INSPECTOR,
                billing_period=BillingPeriodEnum.YEARLY,
                free_reports_count=free_reports_count,
            )
            session.add(user)
            await session.commit()
            print(f"✅ User '{email}' with role {role} created successfully")
            return True  # noqa: TRY300
        except IntegrityError as e:
            await session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if (
                'unique constraint' in error_msg.lower()
                or 'duplicate key' in error_msg.lower()
            ):
                print(f"❌ Error: User with email '{email}' already exists")
            else:
                print(f'❌ Database error: {error_msg}')
            return False
        except Exception as e:
            await session.rollback()
            print(f'❌ Unexpected error: {e}')
            return False


async def main() -> None:  # noqa: D103
    admin_emails = [
        'admin@gmail.com',
        'kadomtsev_admin@gmail.com',
        'kalnyi_admin@gmail.com',
        'grytskiv_admin@gmail.com',
        'kryvtsun_admin@gmail.com',
    ]
    manager_emails = [
        'manager@gmail.com',
        'kadomtsev_manager@gmail.com',
        'kalnyi_manager@gmail.com',
        'grytskiv_manager@gmail.com',
        'kryvtsun_manager@gmail.com',
    ]
    inspector_emails = [
        'inspector@gmail.com',
        'kadomtsev_inspector@gmail.com',
        'kalnyi_inspector@gmail.com',
        'grytskiv_inspectorn@gmail.com',
        'kryvtsun_inspectorn@gmail.com',
    ]
    solo_emails = [
        'solo@gmail.com',
        'kadomtsev_solo@gmail.com',
        'kalnyi_solo@gmail.com',
        'grytskiv_solo@gmail.com',
        'kryvtsun_solo@gmail.com',
    ]
    password = 'qwerty123'
    for email in admin_emails:
        await create_user(email, password, UserRoleEnum.ADMIN, free_reports_count=500)
    for email in manager_emails:
        await create_user(email, password, UserRoleEnum.MANAGER, free_reports_count=500)
    for email in inspector_emails:
        await create_user(email, password, UserRoleEnum.INSPECTOR, free_reports_count=500)
    for email in solo_emails:
        await create_user(email, password, UserRoleEnum.SOLO_OPERATOR, free_reports_count=500)
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
