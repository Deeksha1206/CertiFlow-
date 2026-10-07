import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


os.environ["CERTIFLOW_BASE_URL"] = "http://testserver"
os.environ["DATABASE_URL"] = "sqlite:///./test_certiflow.db"
