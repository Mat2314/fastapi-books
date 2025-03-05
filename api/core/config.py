from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str = "mat"
    POSTGRES_PASSWORD: str = "supersecretpassword"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "8989"
    POSTGRES_DB: str = "fabooks"

    class Config:
        case_sensitive = True


settings = Settings()
