from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OCRSettings(BaseSettings):

    base_url: str = Field("https://api.ocr.space/parse/image", env="BASE_URL")
    api_key: str = Field("your api key", env="API_KEY")
    timeout: int = Field(60, env="TIMEOUT")
    language: str = Field("eng", env="LANGUAGE")
    engine: int = Field(1, env="ENGINE")
    scale: bool = Field(True, env="SCALE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="OCR_",
        case_sensitive=False,
        frozen=True,
        extra="ignore",
    )
