from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

_ph = PasswordHasher() 

def hashear_password(password: str):
    return _ph.hash(password)

def verificar_password(password: str, hash: str):
    try:
        return _ph.verify(hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False