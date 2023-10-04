import os
from dotenv import load_dotenv

def load_environment_variables():
    load_dotenv("keys.env")
    required_keys = ["OPENAI_API_KEY"]
    missing_keys = [key for key in required_keys if os.getenv(key) is None]
    if missing_keys:
        raise Exception(f"{', '.join(missing_keys)} not found")
    else:
        os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
