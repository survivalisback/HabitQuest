from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(password: str, stored: str) -> bool:
    return _pwd_context.verify(password, stored)


@dataclass(frozen=True)
class JwtConfig:
    secret: str
    issuer: str
    expires_in_seconds: int


def generate_jwt(user_id: int, config: JwtConfig) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),
        "iss": config.issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=config.expires_in_seconds)).timestamp()),
    }
    return jwt.encode(payload, config.secret, algorithm="HS256")


def verify_jwt(token: str, config: JwtConfig) -> int | None:
    try:
        payload = jwt.decode(token, config.secret, algorithms=["HS256"], issuer=config.issuer)
        return int(payload.get("sub"))
    except JWTError:
        return None
