import os
from dotenv import load_dotenv

# Load environment variables from .env file once
load_dotenv()

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8001")
BASE_API_URL = f"{FASTAPI_URL}/api/v1"

EMPLOYEE_API_URL = f"{BASE_API_URL}/employees"
PAYROLL_API_URL = f"{BASE_API_URL}/payroll"
