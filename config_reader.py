from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr для конфиденциальных данных
    bot_token: SecretStr
    openrouter_api_key: SecretStr

    # настройки класса настроек задаются через model_config
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()