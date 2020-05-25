from .Base import Base


class General(Base):
    @classmethod
    async def api_status(cls, session):
        return await cls._get(session, "status")

    @classmethod
    async def list_available_statuses(cls, session):
        return await cls._get(session, "statuses")

    @classmethod
    async def list_available_user_roles(cls, session):
        return await cls._get(session, "roles")

    @classmethod
    async def list_accepted_mime_types(cls, session):
        return await cls._get(session, "mimes")

    @classmethod
    async def verify_token(cls, session):
        return await cls._get(session, "auth")
