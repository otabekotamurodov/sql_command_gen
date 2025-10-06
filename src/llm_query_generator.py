import subprocess
import re
import json
from textwrap import dedent

OLLAMA_MODEL = "gemma3:4b"

SCHEMA_DDL = dedent("""
    -- SQLite schema (reference only)
    -- Clients(id INTEGER PK, name TEXT, birth_date TEXT(YYYY-MM-DD), region TEXT)
    -- Accounts(id INTEGER PK, client_id INTEGER FK->Clients.id, balance REAL, open_date TEXT(YYYY-MM-DD))
    -- Transactions(id INTEGER PK, account_id INTEGER FK->Accounts.id, amount REAL, date TEXT(YYYY-MM-DD), type TEXT[credit|debit|transfer])
""").strip()

SYSTEM_RULES = dedent(f"""
    Sen SQL generator assistentsan. Vazifa: foydalanuvchi kiritgan oddiy savoldan
    SQLITE dialektda faqat SELECT query yozish. DELETE/UPDATE/INSERT/DDL YO'Q.

    Qoidalar:
    1) Faqat bitta SELECT query qaytar.
    2) Jadval nomlari: Clients, Accounts, Transactions.
    3) Sanalar TEXT sifatida 'YYYY-MM-DD' ko'rinishida saqlangan.
    4) Aggregatsiya kerak bo'lsa: SUM/AVG/COUNT, GROUP BY ni to'g'ri qo'lla.
    5) Region, oy/yil filtrlarida BETWEEN yoki strftime ishlat.
    6) Natijani LIMIT bilan cheklama, foydalanuvchi so'ramasa hammasini chiqar.
    7) Yozuv faqat SQL, ortiqcha matn yo'q. Agar kod blok ishlatsang, ```sql ... ``` formatida bo'lsin.
    8) Faqat mavjud ustunlardan foydalansang: 
       Clients(id,name,birth_date,region)
       Accounts(id,client_id,balance,open_date)
       Transactions(id,account_id,amount,date,type)

    Kontekst:
    {SCHEMA_DDL}
""").strip()

FEW_SHOTS = [
    {
        "user": "2024 yil iyun oyida Toshkent viloyati bo'yicha jami tranzaksiyalar summasini ko'rsat",
        "sql": dedent("""
                      SELECT c.region,
                             SUM(t.amount) AS total_amount
                      FROM Transactions t
                               JOIN Accounts a ON a.id = t.account_id
                               JOIN Clients c ON c.id = a.client_id
                      WHERE c.region = 'Toshkent'
                        AND strftime('%Y', t.date) = '2024'
                        AND strftime('%m', t.date) = '06'
                      GROUP BY c.region;
                      """).strip()
    },
    {
        "user": "Andijon viloyati bo‘yicha 2023 yildagi o‘rtacha balans",
        "sql": dedent("""
                      SELECT c.region,
                             AVG(a.balance) AS avg_balance_2023
                      FROM Accounts a
                               JOIN Clients c ON c.id = a.client_id
                      WHERE c.region = 'Andijon'
                        AND strftime('%Y', a.open_date) = '2023'
                      GROUP BY c.region;
                      """).strip()
    },
    {
        "user": "2024-01-01 dan 2024-03-31 gacha debit tranzaksiyalar soni va summasi",
        "sql": dedent("""
                      SELECT t.type,
                             COUNT(*)      AS tx_count,
                             SUM(t.amount) AS total_amount
                      FROM Transactions t
                      WHERE t.type = 'debit'
                        AND t.date BETWEEN '2024-01-01' AND '2024-03-31'
                      GROUP BY t.type;
                      """).strip()
    },
]


def _build_prompt(nl_prompt: str) -> str:
    shots = []
    for s in FEW_SHOTS:
        shots.append(
            f"User: {s['user']}\nSQL:\n{s['sql']}\n"
        )
    shots_text = "\n".join(shots)

    final_prompt = dedent(f"""
        [SYSTEM]
        {SYSTEM_RULES}

        [GUIDE EXAMPLES]
        {shots_text}

        [USER]
        {nl_prompt}

        [ASSISTANT]
        Faqat bitta SELECT SQL qaytar. Agar kod blok ishlatsang, ```sql bilan och va ``` bilan yop.
    """).strip()
    return final_prompt


def _run_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout_sec: int = 60) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout_sec
        )
        if result.returncode != 0:
            raise RuntimeError(f"Ollama error: {result.stderr.strip() or result.stdout.strip()}")
        return result.stdout
    except FileNotFoundError:
        raise RuntimeError("Ollama topilmadi. O'rnat: https://ollama.ai va modelni yukla: `ollama pull gemma3:4b`")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Ollama javobi vaqt bo'yicha o‘tdi (timeout). Model yoki promptni yengillashtiring.")


def _extract_sql(text: str) -> str:
    # ```sql ... ``` blok
    block = re.search(r"```sql\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if block:
        candidate = block.group(1).strip()
        if candidate:
            return candidate

    m = re.search(r"(SELECT\b[\s\S]+)", text, flags=re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
        semi = candidate.find(";")
        if semi != -1:
            candidate = candidate[:semi + 1]
        return candidate

    return ""


def _clean_sql(sql: str) -> str:
    # faqat SELECT ga ruxsat
    lowered = re.sub(r"\s+", " ", sql).strip().lower()
    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "truncate ", "create "]
    if any(tok in lowered for tok in forbidden):
        raise ValueError("Faqat SELECT ruxsat. Model noto'g'ri query yaratdi.")

    sql = sql.strip()
    if not sql.endswith(";"):
        sql += ";"
    return sql


def generate_sql(nl_prompt: str, model: str = OLLAMA_MODEL) -> str:
    prompt = _build_prompt(nl_prompt)
    raw = _run_ollama(prompt, model=model)
    sql = _extract_sql(raw)

    if not sql:
        sql = dedent("""
                     SELECT COUNT(*) AS total_rows
                     FROM Clients;
                     """).strip()

    sql = _clean_sql(sql)
    return sql


# ---- CLI test ----
if __name__ == "__main__":
    tests = [
        "2024 yil iyun oyida Toshkent bo‘yicha jami tranzaksiyalar summasini ko'rsat",
        "Andijon viloyati bo‘yicha 2023 yildagi o‘rtacha balansni top",
        "2024-01-01 dan 2024-03-31 gacha debit tranzaksiyalar soni va summasi",
        "Farg‘ona viloyati bo‘yicha 2024 yil may oyidagi kredit tranzaksiyalar yig'indisi"
    ]
    for q in tests:
        print("\nUSER:", q)
        try:
            sql = generate_sql(q)
            print("SQL:\n", sql)
        except Exception as e:
            print("ERR:", e)
