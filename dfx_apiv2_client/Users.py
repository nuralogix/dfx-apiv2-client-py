import datetime
from .Settings import Settings
from .Base import Base


class Users(Base):
    url_fragment = "users"

    @classmethod
    async def create(cls, session, first_name: str, last_name: str, email: str, password: str, phone_number: str,
                     gender: str, date_of_birth: datetime.date, height_cm: int, weight_kg: int):
        data = {
            "FirstName": str(first_name),
            "LastName": str(last_name),
            "Email": str(email).lower(),
            "Password": str(password),
            "PhoneNumber": str(phone_number),
            "Gender": str(gender).lower(),
            "DateOfBirth": date_of_birth.strftime("%Y-%m-%d"),
            "HeightCm": str(height_cm),
            "WeightKg": str(weight_kg)
        }

        return await cls.post(session, cls.url_fragment, data=data)

    @classmethod
    async def login(cls, session, email: str, password: str):
        data = {
            "Email": email,
            "Password": password,
        }

        body = await cls.post(session, f"{cls.url_fragment}/auth", data=data)

        Settings.user_token = body["Token"]

        return body

    @classmethod
    async def retrieve(cls, session):
        return await cls.get(session, cls.url_fragment)
