from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres techniques de l'application, lus depuis l'environnement.

    Ne pas confondre avec le module métier `app.configuration`, qui gérera
    les règles, seuils et listes noires (voir docs/architecture_logicielle.md,
    section 4.10). Cette classe ne couvre que les réglages nécessaires au
    démarrage de l'application (nom, version, base de données, CORS).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_name: str = "IDS - Centre Cinématographique Marocain"
    version: str = "1.0.0"
    app_env: str = "development"

    database_url: str = ""
    cors_origins: str = "http://localhost:5173"

    # Authentification (voir docs/conception_api_rest.md, section 5 et
    # docs/preparation_implementation.md, section 3.4 pour la durée de session)
    secret_key: str = "changez-moi-en-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
