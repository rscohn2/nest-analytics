from os import getenv

from dotenv import load_dotenv

load_dotenv(dotenv_path=".portal_env")
print(f"Nest project id: {getenv('NEST_PROJECT_ID')}")
