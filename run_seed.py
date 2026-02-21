import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL not set in .env file", file=sys.stderr)
    sys.exit(1)

print("Connecting to database...")
try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()

    print("Reading seed.sql...")
    with open('seed.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Executing SQL...")
    cursor.execute(sql)

    print("Success! Data seeded.")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
