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

    print("Reading schema.sql...")
    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Creating tables...")
    cursor.execute(sql)

    print("Success! Tables created.")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
