from typing import Any

from sqlalchemy import func, select

from core.dao import BaseDAO
from dto import (
    AvailableNowDTO,
    CreateInspectorDTO,
    InspectorDashboardDTO,
    OnSiteTodayDTO,
    ReportsPendingDTO,
    TotalInspectorsDTO,
)
from models import Inspector


class InspectorDAO(BaseDAO):
    """DAO for User model."""

    async def create(
        self,
        *,
        inspector_data: CreateInspectorDTO,
    ) -> Inspector:
        inspector = Inspector(
            name=inspector_data.name,
            surname=inspector_data.surname,
            email=inspector_data.email,
            phone_number=inspector_data.phone_number,
            license_number=inspector_data.license_number,
            licence_type=inspector_data.licence_type,
            issue_date=inspector_data.issue_date,
            expiration_date=inspector_data.expiration_date,
            license_image_keys=inspector_data.license_image_keys or None,
        )
        self._session.add(inspector)
        await self._session.flush()
        await self._session.refresh(inspector)
        return inspector

    async def get_all(
        self, page: int, limit: int
    ) -> tuple[list[Inspector], int]:
        query = select(Inspector)
        return await self.paginate(query=query, page=page, limit=limit)

    async def get_by_id(self, inspector_id: int) -> Inspector | None:
        stmt = select(Inspector).where(
            Inspector.id == inspector_id, Inspector.is_active == True
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_by_id(
        self,
        inspector_id: int,
        update_data: dict[str, Any],
    ) -> Inspector | None:
        """Update inspector by id."""
        inspector = await self.get_by_id(inspector_id)
        if not inspector:
            return None
        for key, value in update_data.items():
            if hasattr(inspector, key):
                setattr(inspector, key, value)
        await self._session.flush()
        await self._session.refresh(inspector)
        return inspector

    async def get_inspectors_dashboard(
        self,
        user_id: int,
    ) -> InspectorDashboardDTO:
        """Get aggregated inspectors dashboard.

        TODO: Make metrics user-specific when requirements are defined.
        TODO: Replace mocked on_site_today, available_now and reports_pending
        with real data when scheduling and reporting models are available.
        """
        total_stmt = select(func.count(Inspector.id)).where(
            Inspector.is_active == True  # noqa: E712
        )
        total_result = await self._session.execute(total_stmt)
        total_inspectors_count = int(total_result.scalar_one() or 0)

        names_stmt = (
            select(Inspector)
            .where(Inspector.is_active == True)  # noqa: E712
            .order_by(Inspector.created_at.desc())
            .limit(3)
        )
        names_result = await self._session.execute(names_stmt)
        inspectors = list(names_result.scalars().all())
        inspector_names = [inspector.full_name for inspector in inspectors]

        total_inspectors = TotalInspectorsDTO(
            amount=total_inspectors_count,
            inspector_names=inspector_names,
        )

        on_site_today = OnSiteTodayDTO(
            amount=0,
            inspector_names=[],
        )

        available_now = AvailableNowDTO(
            amount=0,
            inspector_names=[],
        )

        reports_pending = ReportsPendingDTO(
            amount=0,
            report_names=[],
        )

        return InspectorDashboardDTO(
            total_inspectors=total_inspectors,
            on_site_today=on_site_today,
            available_now=available_now,
            reports_pending=reports_pending,
        )
