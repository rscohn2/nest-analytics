# This module is used to resolve circular dependencies. It cannot import from
# other modules in the application.

from os import getenv

from dotenv import load_dotenv

load_dotenv(dotenv_path=".portal_env")
print(f"Nest project id: {getenv('NEST_PROJECT_ID')}")
