from typing import Union

from .Base import Base


class Profiles(Base):
    url_fragment = "users/profiles"

    @classmethod
    async def create(cls, session, name: str, email: str):
        data = {
            "Name": name,
            "Email": email,
        }

        body = await cls._post(session, cls.url_fragment, data=data)

        return body["ID"]

    @classmethod
    async def update(cls, session, profile_id: str):
        # TODO: Does not have a data?
        return await cls._patch(session, f"{cls.url_fragment}/{profile_id}", data={})

    @classmethod
    async def delete(cls, session, profile_id: str):
        return await cls._delete(session, f"{cls.url_fragment}/{profile_id}")

    @classmethod
    async def retrieve(cls, session, profile_id: str):
        return await cls._get(session, f"{cls.url_fragment}/{profile_id}")

    @classmethod
    # TODO; What is user_profile_name here, is it email
    async def list(cls, session, user_profile_name: str = "", status: str = "", limit: int = 25, offset: int = 0):
        """[summary]

        Keyword Arguments:
            user_profile_name {str} -- filter by a Profile Name (default: {None})
            status {str} -- filter by Profile Status (default: {None})
            limit {int} -- Number of measurement records to return (default: {25})
            offset {int} -- Offset to specify the start of the count (default: {0})

        Returns:
            [type] -- [description]
        """
        params = {}
        if user_profile_name:
            params["UserProfileName"] = user_profile_name
        if status:
            params["Status"] = status
        if limit:
            params["Limit"] = limit
        if offset:
            params["Offset"] = offset

        return await cls._get(session, cls.url_fragment, params=params)

    @classmethod
    async def list_by_user(cls, session, user_profile_id, user_profile_name: str = "", status: str = "", limit: int = 25, offset: int = 0):
        """[summary]

        Keyword Arguments:
            user_profile_id {str} -- filter by Profile ID
            user_profile_name {str} -- filter by a Profile Name (default: {None})
            status {str} -- filter by Profile Status (default: {None})
            limit {int} -- Number of measurement records to return (default: {25})
            offset {int} -- Offset to specify the start of the count (default: {0})

        Returns:
            [type] -- [description]
        """
        params = {}
        if user_profile_name:
            params["UserProfileName"] = user_profile_name
        if status:
            params["Status"] = status
        if limit:
            params["Limit"] = limit
        if offset:
            params["Offset"] = offset

        return await cls._get(session, f"users/{user_profile_id}/profiles", params=params)
