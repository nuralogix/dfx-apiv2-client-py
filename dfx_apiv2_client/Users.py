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
            "WeightKg": str(weight_kg),
        }

        return await cls._post(session, cls.url_fragment, data=data)

    @classmethod
    async def login(cls, session, email: str, password: str):
        data = {
            "Email": email,
            "Password": password,
        }

        body = await cls._post(session, f"{cls.url_fragment}/auth", data=data)

        Settings.user_token = body["Token"]

        return body

    @classmethod
    async def request_phone_login_code(cls, session, org_key: str, phone_number: str):
        return await cls._get(session, f"{cls.url_fragment}/auth/code/{org_key}/{phone_number}")

    @classmethod
    async def login_with_phone_code(cls, session, org_key: str, phone_number: str, login_code: str):
        data = {
            "LoginCode": str(login_code),
            "PhoneNumber": str(phone_number),
            "OrgKey": str(org_key),
        }

        body = await cls._post(session, f"{cls.url_fragment}/auth/code", data=data)

        Settings.user_token = body["Token"]

        return body

    @classmethod
    async def retrieve(cls, session):
        return await cls._get(session, cls.url_fragment)

    @classmethod
    async def update(cls, session, first_name: str, last_name: str, email: str, password: str, phone_number: str,
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
            "WeightKg": str(weight_kg),
        }

        return await cls._patch(session, cls.url_fragment, data=data)

    @classmethod
    async def retrieve_user_role(cls, session):
        return await cls._get(session, f"{cls.url_fragment}/role")

    @classmethod
    async def send_password_reset_request(cls, session, email: str, org_id: str):
        data = {
            "Email": str(email),
            "Identifier": str(org_id),
        }

        return await cls._patch(session, f"{cls.url_fragment}/sendreset", data=data)

    @classmethod
    async def reset_password(cls, session, reset_token, new_password):
        data = {
            "ResetToken": str(reset_token),
            "Password": str(new_password),
        }

        return await cls._patch(session, f"{cls.url_fragment}/reset", data=data)

    @classmethod
    async def send_account_verification_code(cls, session, user_id):
        return await cls._post(session, f"{cls.url_fragment}/verificationCode/{user_id}", {})

    @classmethod
    async def verify_user_account(cls, session, verification_code, user_id):
        data = {
            "VerificationCode": verification_code,
            "ID": user_id,
        }

        return await cls._post(session, f"{cls.url_fragment}/verify", data=data)

    @classmethod
    async def remove(cls, session):
        return await cls._delete(session, cls.url_fragment)
