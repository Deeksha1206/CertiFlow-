import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


CERTIFLOW_BASE_URL = os.getenv(
    "CERTIFLOW_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


GENERATED_CERTIFICATES_DIR = (
    BASE_DIR / "generated_certificates"
)

TEMPLATES_DIR = BASE_DIR / "templates"


GENERATED_CERTIFICATES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TEMPLATES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
