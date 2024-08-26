from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List, Optional

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    expire_token_minutes: int = 30
    
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    email_from: str
    email_subject: str = "Your Subject Here"
    
    allowed_hosts: List[AnyHttpUrl] = ["http://localhost:3000", "http://localhost"]
    
    log_level: str = "info"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()




