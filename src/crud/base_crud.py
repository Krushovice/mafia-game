from typing import Type, TypeVar, Generic, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base

ModelType = TypeVar("ModelType", bound=declarative_base())

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, session: AsyncSession, obj_in: dict) -> ModelType:
        return await self.create(session, obj_in, commit=True)

    async def create(self, session: AsyncSession, obj_in: dict, commit: bool = True) -> ModelType:
        obj = self.model(**obj_in)
        session.add(obj)
        if commit:
            await session.commit()
            await session.refresh(obj)
        return obj

    async def get(self, session: AsyncSession, obj_id: int) -> ModelType | None:
        result = await session.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def list(self, session: AsyncSession) -> List[ModelType]:
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def update(self, session: AsyncSession, obj_id: int, obj_in: dict) -> ModelType | None:
        return await self.update(session, obj_id, obj_in, commit=True)

    async def update(self, session: AsyncSession, obj_id: int, obj_in: dict, commit: bool = True) -> ModelType | None:
        obj = await self.get(session, obj_id)
        if not obj:
            return None
        for field, value in obj_in.items():
            setattr(obj, field, value)
        if commit:
            await session.commit()
            await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj_id: int) -> bool:
        return await self.delete(session, obj_id, commit=True)

    async def delete(self, session: AsyncSession, obj_id: int, commit: bool = True) -> bool:
        obj = await self.get(session, obj_id)
        if not obj:
            return False
        await session.delete(obj)
        if commit:
            await session.commit()
        return True