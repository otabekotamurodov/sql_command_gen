import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta
from tqdm import tqdm
import os

os.makedirs("data", exist_ok=True)
DB_PATH = "data/bank.db"

#  Faker obyekt
fake = Faker("uz_UZ")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
                  DROP TABLE IF EXISTS Transactions;
                  DROP TABLE IF EXISTS Accounts;
                  DROP TABLE IF EXISTS Clients;

                  CREATE TABLE Clients
                  (
                      id         INTEGER PRIMARY KEY AUTOINCREMENT,
                      name       TEXT,
                      birth_date TEXT,
                      region     TEXT
                  );

                  CREATE TABLE Accounts
                  (
                      id        INTEGER PRIMARY KEY AUTOINCREMENT,
                      client_id INTEGER,
                      balance   REAL,
                      open_date TEXT,
                      FOREIGN KEY (client_id) REFERENCES Clients (id)
                  );

                  CREATE TABLE Transactions
                  (
                      id         INTEGER PRIMARY KEY AUTOINCREMENT,
                      account_id INTEGER,
                      amount     REAL,
                      date       TEXT,
                      type       TEXT,
                      FOREIGN KEY (account_id) REFERENCES Accounts (id)
                  );
                  """)

conn.commit()

# 🧍 1. Clients generatsiya
NUM_CLIENTS = 100_000
regions = [
    "Toshkent", "Andijon", "Farg‘ona", "Namangan",
    "Samarqand", "Buxoro", "Xorazm", "Qashqadaryo",
    "Surxondaryo", "Jizzax", "Navoiy", "Sirdaryo", "Qoraqalpog‘iston"
]

clients_data = []
for _ in tqdm(range(NUM_CLIENTS), desc="Generating clients"):
    clients_data.append((
        fake.name(),
        fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        random.choice(regions)
    ))
cur.executemany("INSERT INTO Clients (name, birth_date, region) VALUES (?, ?, ?)", clients_data)
conn.commit()

# 💳 2. Accounts generatsiya
NUM_ACCOUNTS = 200_000
accounts_data = []
for _ in tqdm(range(NUM_ACCOUNTS), desc="Generating accounts"):
    client_id = random.randint(1, NUM_CLIENTS)
    balance = round(random.uniform(1000, 10_000_000), 2)
    open_date = (datetime.now() - timedelta(days=random.randint(0, 2000))).isoformat()
    accounts_data.append((client_id, balance, open_date))
cur.executemany("INSERT INTO Accounts (client_id, balance, open_date) VALUES (?, ?, ?)", accounts_data)
conn.commit()

# 💸 3. Transactions generatsiya
NUM_TRANSACTIONS = 700_000
transaction_types = ["credit", "debit", "transfer"]

transactions_data = []
for _ in tqdm(range(NUM_TRANSACTIONS), desc="Generating transactions"):
    account_id = random.randint(1, NUM_ACCOUNTS)
    amount = round(random.uniform(10_000, 10_000_000), 2)
    date = (datetime.now() - timedelta(days=random.randint(0, 730))).isoformat()
    t_type = random.choice(transaction_types)
    transactions_data.append((account_id, amount, date, t_type))

batch_size = 50_000
for i in tqdm(range(0, len(transactions_data), batch_size), desc="Saving to DB"):
    batch = transactions_data[i:i + batch_size]
    cur.executemany("INSERT INTO Transactions (account_id, amount, date, type) VALUES (?, ?, ?, ?)", batch)
    conn.commit()

conn.close()
print("✅ Database created successfully: data/bank.db")
