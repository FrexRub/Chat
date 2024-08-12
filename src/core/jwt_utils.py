from fastapi import Response
import bcrypt
import jwt

from config import setting, COOKIE_NAME


def create_hash_password(password: str) -> bytes:
    """
    Создание хеш пароля
    :param password: str
        пароль
    :return: bytes
        хеш значение пароля
    """
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    """
    Проверка валидности пароля. Проверяет пароль с хеш-значением правильного пароля
    :param password: str
        переданный пароль
    :param hashed_password: bytes
        хеш-значение правильного пароля
    :return: bool
        возвращает True, если пароль верный иначе - False
    """
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def encode_jwt(
    payload: dict,
    private_key: str = setting.auth_jwt.private_key_path.read_text(),
    algorithm: str = setting.auth_jwt.algorithm,
):
    """
     Создает jwt-токена по алгоритму RS256 (с использованием ассиметричных ключей)
    :param payload: dict
        содержание jwt-токена
    :param private_key: str
        приватный ключ
    :param algorithm: str
        задается алгоритм
    :return:
        возвращает jwt-токен
    """
    encoded = jwt.encode(payload, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = setting.auth_jwt.public_key_path.read_text(),
    algorithm: str = setting.auth_jwt.algorithm,
):
    """
        Раскодирует jwt-токен
    :param token: str | bytes
        jwt-токен
    :param public_key: str
        открытый ключ шифрования
    :param algorithm: str
        алгоритм шифрования
    :return:
        ?? содержание токена (payload)
    """
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded


def set_cookie(
    response: Response,
    token: str,
) -> None:
    """
        Устанавливает куки с jwt-токеном
    :param response:
    :param token:
    :return:
    """
    response.set_cookie(key=COOKIE_NAME, value=token, httponly=True)
