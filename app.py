from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
from dotenv import load_dotenv

# Только для локальной разработки
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# Берём переменные окружения
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_NAME = os.getenv("FROM_NAME", "Rustem")

# Проверка наличия ключей
if not BREVO_API_KEY or not FROM_EMAIL:
    print("WARNING: BREVO_API_KEY или FROM_EMAIL не установлены!")

def send_email(to_email: str, subject: str, text: str, html: str | None = None):
    """Отправка письма через Brevo SMTP API"""
    if not BREVO_API_KEY:
        raise ValueError("BREVO_API_KEY не задан!")

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text,
        "htmlContent": html or text
    }

    response = requests.post(url, json=data, headers=headers, timeout=15)
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            flash("Введите email.", "warning")
            return redirect(url_for("index"))

        try:
            resp = send_email(
                to_email=email,
                subject="Привет от Рустема",
                text="Привет от Рустема",
                html="<p>Привет от Рустема</p>"
            )

            print("======== BREVO API RESPONSE ========")
            print("Status code:", resp.status_code)
            print("Response body:", resp.text)
            print("===================================")

            if resp.status_code in [200, 201, 202]:
                flash("Письмо успешно отправлено!", "success")
            else:
                flash(f"Ошибка при отправке: {resp.text}", "danger")

        except Exception as e:
            print("Ошибка при отправке письма:", e)
            flash(f"Ошибка при отправке: {e}", "danger")

        return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
