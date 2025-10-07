
# 🧠 AI Data Analyst Assistant

### Lokal LLM asosida bank ma’lumotlarini tahlil qiluvchi tizim

---

## 📘 Loyihaning maqsadi

Ushbu tizim foydalanuvchining oddiy **tabiiy tildagi so‘rovini** (masalan:

> “2024 yil iyun oyida Toshkentdagi tranzaksiyalar summasini ko‘rsat”)

avtomatik ravishda **SQL so‘rovga** aylantiradi, uni ma’lumotlar bazasida bajaradi va **Excel fayl ko‘rinishida grafik bilan** natija qaytaradi.

---

## ⚙️ Texnologiyalar

| Qism                     | Texnologiya                          |
| ------------------------ | ------------------------------------ |
| Dasturlash tili          | Python 3.10+                         |
| LLM modeli               | Gemma3:4b (Ollama orqali)            |
| Ma’lumotlar bazasi       | SQLite                               |
| Kutubxonalar             | Flask, Faker, Pandas, OpenPyXL, TQDM |
| Diagramma vositasi       | Matplotlib / OpenPyXL chart          |
| Foydalanuvchi interfeysi | Web UI (Flask)                       |

---

## 📦 O‘rnatish bo‘yicha qo‘llanma

### 1️⃣ Repozitoriyani klonlash yoki fayllarni yuklab olish

```bash
git clone https://github.com/otabekotamurodov/sql_command_gen.git
cd sql_command_gen
```

### 2️⃣ Virtual muhit yaratish va faollashtirish

```bash
python -m venv venv
venv\Scripts\activate       # (Windows)
# yoki
source venv/bin/activate    # (Linux/Mac)
```

### 3️⃣ Kutubxonalarni o‘rnatish

```bash
pip install -r requirements.txt
```

### 4️⃣ LLM modelni o‘rnatish (Ollama)

* [https://ollama.ai](https://ollama.ai) saytiga kirib Ollama dasturini o‘rnating.
* So‘ng terminalda quyidagini yozing:

```bash
ollama pull gemma3:4b
```

### 5️⃣ Ma’lumotlar bazasini yaratish

```bash
python src/generate_data.py
```

👉 Bu skript 1 million yozuvdan iborat soxta (mock) ma’lumotlar bazasini `data/bank.db` faylida yaratadi.

---

Agar, baza yaratish kerak bo'lmasa shunchaki bank.db file ni `src/data/` ichiga joylashtiring

---

## 🚀 Tizimni ishga tushirish

```bash
python src/app.py
```

Keyin brauzerda oching:
🔗 `http://127.0.0.1:8008`

---

## 💬 Foydalanish

1. Web sahifada sizga input maydon chiqadi.
2. O‘sha joyga tabiiy tildagi savolni yozing, masalan:

   ```
   2023 va 2024 yillardagi kredit tranzaksiyalar o‘sish foizini har bir viloyat bo‘yicha ko‘rsat
   ```
3. “Natija olish” tugmasini bosing.
4. Tizim avtomatik SQL yaratadi, uni bajaradi va Excel faylni yuklab olish uchun tugma beradi.
5. Fayl ichida jadval + grafik mavjud bo‘ladi.

---

## 🧩 Sinov uchun namunaviy so‘rovlar

| № | So‘rov (Prompt)                                                                   |
| - | --------------------------------------------------------------------------------- |
| 1 | 2023 yil davomida har bir viloyat bo‘yicha jami tranzaksiyalar summasini aniqlang |
| 2 | 2024 yil yanvar oyida debit tranzaksiyalar soni va o‘rtacha summasini ko‘rsating  |
| 3 | 2023–2024 yillarda kredit va debit hajmlarini choraklar kesimida solishtiring     |
| 4 | Har bir region uchun mijozlar soni va o‘rtacha balansni chiqar                    |
| 5 | 2024 yilning har oyidagi o‘rtacha balans va jami tranzaksiya summasini ko‘rsat    |
| 6 | Eng faol 10 ta mijozni toping                                                     |
| 7 | 2023 va 2024 yillardagi kredit o‘sish foizini hisoblang                           |
| 8 | Regionlar bo‘yicha balanslarning ulushi (%) ni chiqaring                          |

---

## 📊 Natija

* Har bir so‘rovdan so‘ng tizim quyidagilarni hosil qiladi:

  * Avtomatik SQL query
  * Excel fayl (`results/` papkada saqlanadi)
  * Grafik (bar/pie/line chart)

Excel misol:

```
region        total_amount
Toshkent      27228099640.43
Samarqand     27552364389.81
...
```

Va diagramma avtomatik yaratiladi.

---

## 🛠 Papka tuzilmasi

```
project_root/
├── data/
│   └── bank.db                # 1 mln yozuvli mock baza
├── results/                   # Excel natijalar
├── src/
│   ├── generate_data.py       # Ma’lumotlar yaratish
│   ├── llm_query_generator.py # LLM -> SQL
│   ├── run_query.py           # SQL bajarish
│   ├── export_excel.py        # Excel va diagramma
│   └── app.py                 # Web interfeys
├── requirements.txt
└── README.md
```

---

## ⚡ Muammolarni yechish

| Muammo                | Sabab / Yechim                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------ |
| `Ollama topilmadi`    | Ollama dasturi o‘rnatilmagan. [https://ollama.ai](https://ollama.ai) dan yuklab oling.           |
| `Database topilmadi`  | `generate_data.py` ishlamagan. Avval uni ishga tushiring.                                        |
| `Bo‘sh DataFrame`     | Siz kiritgan so‘rovga mos ma’lumot topilmadi.                                                    |
| `Excel yozishda xato` | `results/` papka mavjud emas – fayl avtomatik yaratiladi, lekin qo‘lda ham yaratishingiz mumkin. |

---

## 👨‍💻 Mualliflar va aloqa

Loyiha AI Developer Test vazifasi uchun yaratilgan.
Muallif: **AI Developer Team**
Aloqa: `support@ai-analyst.local`

---

Xohlaysanmi, shu README’ni men hozir `README.md` fayl formatida tayyorlab beray (ya’ni tayyor Markdown versiya qilib beraman)?
Shunda uni to‘g‘ridan-to‘g‘ri GitHub yoki loyihaning ildiz papkasiga qo‘yish mumkin bo‘ladi.
