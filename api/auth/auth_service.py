from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime, timedelta, timezone
import jwt
from typing import Dict, Any
from user.user import User
from user.user_repository import UserRepository

class AuthService:
    def __init__(
        self,
        google_client_id: str,
        jwt_secret: str,
        jwt_algorithm: str = "HS256",
        access_token_expire_minutes: int = 1440
    ):
        self.google_client_id = google_client_id
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.user_repository = UserRepository()

    async def verify_google_token(self, id_token_str: str) -> str:
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                requests.Request(), 
                self.google_client_id
            )
            email = idinfo['email']
            user = await self._get_or_create_user(email, idinfo)
            access_token = self._create_access_token(user)

            return access_token

        except Exception as e:
            raise Exception(f"Invalid token: {str(e)}")

    async def _get_or_create_user(self, email: str, idinfo: Dict[str, Any]) -> User:
        user = await self.user_repository.find_by_email(email)
        if not user:
            user = await self.user_repository.create({
                "id": idinfo["sub"],
                "email": email,
                "name": idinfo.get("name", "")
            })
        else:
            user = await self.user_repository.update_last_login(email)
        return user

    def _create_access_token(self, user: User) -> str:
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expire
        }
        return jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                raise Exception("Invalid token")
            
            user = await self.user_repository.find_by_id(user_id)
            if user is None:
                raise Exception("User not found")
            
            return user
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token") 