from flask import Flask, render_template_string, request, send_file
from llm_query_generator import generate_sql
from run_query import run_query
from export_excel import export_to_excel
import traceback
import os

app = Flask(__name__)

# html code
TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <title>AI Data Analyst Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f3f6fa;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 80px;
        }
        h1 {
            color: #2c3e50;
        }
        form {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 480px;
        }
        textarea {
            width: 100%;
            height: 100px;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 14px;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
        }
        button:hover {
            background: #2980b9;
        }
        .output {
            margin-top: 30px;
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            width: 480px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            word-wrap: break-word;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .error {
            color: red;
        }
        .download-link {
            display: inline-block;
            margin-top: 15px;
            background: #2ecc71;
            color: white;
            padding: 8px 14px;
            text-decoration: none;
            border-radius: 6px;
        }
        .download-link:hover {
            background: #27ae60;
        }
    </style>
</head>
<body>
    <h1>🧠 AI Data Analyst Assistant</h1>
    <form method="POST">
        <label for="prompt">Savol kiriting (masalan: "2024 yil iyun oyida Toshkentdagi tranzaksiyalar summasi")</label><br><br>
        <textarea name="prompt" placeholder="Bu yerga yozing...">{{ prompt or '' }}</textarea><br><br>
        <button type="submit">Natija olish</button>
    </form>

    {% if sql %}
    <div class="output">
        <h3>📜 Yaratilgan SQL:</h3>
        <pre>{{ sql }}</pre>
        {% if excel_file %}
        <a class="download-link" href="/download/{{ excel_file }}">📊 Excelni yuklab olish</a>
        {% endif %}
    </div>
    {% endif %}

    {% if error %}
    <div class="output error">
        <h3>⚠️ Xatolik:</h3>
        <pre>{{ error }}</pre>
    </div>
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    sql = None
    excel_file = None
    error = None
    prompt = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            try:
                # SQL Command gen
                sql = generate_sql(prompt)

                # RUN SQL query
                df = run_query(sql)

                # xlcx
                filename = export_to_excel(df)
                excel_file = os.path.basename(filename)

            except Exception as e:
                error = traceback.format_exc()

    return render_template_string(TEMPLATE, sql=sql, excel_file=excel_file, error=error, prompt=prompt)


@app.route("/download/<path:filename>")
def download(filename):
    filepath = os.path.join("results", filename)
    if not os.path.exists(filepath):
        return "Fayl topilmadi", 404
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8008, debug=True)
