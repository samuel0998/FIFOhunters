import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("Tentando conectar em:")
print(DATABASE_URL)

try:
    conn = psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        connect_timeout=10
    )
    print("✅ CONEXÃO COM O BANCO REALIZADA COM SUCESSO")

    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("✅ QUERY EXECUTADA COM SUCESSO:", cur.fetchone())

    cur.close()
    conn.close()
    print("🔌 Conexão encerrada")

except Exception as e:
    print("❌ FALHA NA CONEXÃO COM O BANCO")
    print(type(e).__name__)
    print(e)
