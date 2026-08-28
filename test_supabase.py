from pathlib import Path
import tomllib

from supabase import create_client


SECRETS_PATH = (
    Path(__file__).resolve().parent
    / ".streamlit"
    / "secrets.toml"
)


with open(SECRETS_PATH, "rb") as file:
    secrets = tomllib.load(file)


supabase = create_client(
    secrets["SUPABASE_URL"],
    secrets["SUPABASE_SECRET_KEY"],
)


response = (
    supabase
    .table("daily_records")
    .select("*")
    .limit(1)
    .execute()
)


print("Supabase connection successful.")
print(f"Rows returned: {len(response.data)}")