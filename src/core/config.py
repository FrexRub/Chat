from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent

DB_PATH = BASE_DIR / "chat.sqlite3"


class DbSetting(BaseSettings):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = False


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "serts" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "serts" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_day: int = 30


class Setting(BaseModel):

    db: DbSetting = DbSetting()

    auth_jwt: AuthJWT = AuthJWT()


setting = Setting()
