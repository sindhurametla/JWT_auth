from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ["argon2"], deprecated = "auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_passwrod: str, hashed_passwrod: str) -> bool:
    return pwd_context.verify(plain_passwrod, hashed_passwrod)

