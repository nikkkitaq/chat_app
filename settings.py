"""File with settings"""
from envparse import Env


env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:54320/chat_app",
)  # connect string for the database

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://postgres_test:postgres_test@0.0.0.0:54321/chat_app_test",
)
