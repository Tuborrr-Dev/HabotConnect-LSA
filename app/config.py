"""**Name:** Israel Adetubo
**Contact:** israetubo@gmail.com"""

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://localhost/habotconnect_dev"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    @staticmethod
    def validate():
        missing = [
            name
            for name in ("SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "JWT_SECRET_KEY")
            if not getattr(ProductionConfig, name)
        ]
        if missing:
            raise RuntimeError(
                f"Missing required production env vars: {', '.join(missing)}"
            )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
