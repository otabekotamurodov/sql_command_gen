import sqlite3
import pandas as pd
import os
from llm_query_generator import generate_sql

DB_PATH = "data/bank.db"


def run_query(sql_query: str) -> pd.DataFrame:
    """
    Berilgan SQL query'ni bajaradi va pandas DataFrame sifatida natijani qaytaradi.
    Agar xato bo'lsa, foydali Exception qaytaradi.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database topilmadi: {DB_PATH}")

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # ⚡ Query bajarish
        df = pd.read_sql_query(sql_query, conn)
        return df
    except Exception as e:
        raise RuntimeError(f"SQL bajarishda xato: {e}")
    finally:
        if conn:
            conn.close()


# ---- CLI test ----
if __name__ == "__main__":
    prompt = "2024 yil may oyida Andijondagi tranzaksiyalar summasini ko‘rsat"
    print("🧠 Foydalanuvchi prompt:", prompt)

    sql_query = generate_sql(prompt)
    print("\n📜 Yaratilgan SQL:\n", sql_query)

    df = run_query(sql_query)
    print("\n✅ Natija (birinchi 5 qator):")
    print(df.head())
