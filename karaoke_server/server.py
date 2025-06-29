
from flask import Flask, request, jsonify           # Flask — библиотека для создания API
from flask_cors import CORS                         # CORS — чтобы приложение (например, на Kivy) могло делать запросы
import psycopg2                                     # Подключение к PostgreSQL
import bcrypt                                       # Для хеширования паролей
import secrets                                      # Для генерации безопасных токенов
import datetime                                     # Для расчёта даты окончания PRO-доступа
import os                                     # Для работы с путями (например, .env)

# --- Запуск Flask-приложения ---
app = Flask(__name__)
CORS(app)  # Разрешаем CORS для запросов с других источников

# --- Данные для подключения к PostgreSQL (твоя база на Render) ---
DB_HOST = "dpg-d1f729ali9vc739mck2g-a"
DB_NAME = "karaoke_h7ks"
DB_USER = "karaoke_h7ks_user"
DB_PASS = "KHWlivhitgGDwPjptwwQuMJzYXEuB9ZI"
DB_PORT = 5432

### проверка сервера
@app.route('/')
def home():
    return "Сервер работает!"


# --- Функция для подключения к базе данных ---
def get_connection():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
    )

# --- Создаём таблицу пользователей (если её ещё нет) ---
def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,               -- Уникальный идентификатор
                name TEXT NOT NULL,                  -- Имя пользователя
                email TEXT UNIQUE NOT NULL,          -- Email (уникален)
                password TEXT NOT NULL,              -- Пароль (в зашифрованном виде)
                token TEXT,                          -- Уникальный токен авторизации
                pro_expires TIMESTAMP                -- До какой даты активна PRO-версия
            );
            """)
            conn.commit()

# --- Вызываем создание таблицы при старте сервера ---
create_table()

# --- Генерация случайного токена (для входа) ---
def generate_token():
    return secrets.token_hex(16)  # возвращает 32-символьный hex-код

# =============================
# 📌 РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
# =============================
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()                     # Получаем данные из тела запроса (JSON)
    name = data.get("name")                       # Получаем имя
    email = data.get("email")                     # Получаем email
    password = data.get("password")               # Получаем пароль

    if not all([name, email, password]):
        return jsonify({"error": "Введите имя, email и пароль"}), 400

    # Хешируем пароль
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    token = generate_token()  # Создаём токен
    pro_expires = datetime.datetime.utcnow() + datetime.timedelta(days=3)  # Пробный период на 3 дня

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO users (name, email, password, token, pro_expires)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING name, token, pro_expires;
                """, (name, email, hashed_pw, token, pro_expires))
                user = cur.fetchone()
                conn.commit()
                return jsonify({
                    "name": user[0],
                    "token": user[1],
                    "pro_expires": user[2].isoformat()  # возвращаем срок действия PRO
                }), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Email уже зарегистрирован"}), 409

# =============================
# 📌 ВХОД ПОЛЬЗОВАТЕЛЯ
# =============================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Введите email и пароль"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, password, token, pro_expires FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                return jsonify({"error": "Пользователь не найден"}), 404

            hashed_pw = user[2]
            if not bcrypt.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8")):
                return jsonify({"error": "Неверный пароль"}), 401

            return jsonify({
                "name": user[1],
                "token": user[3],
                "pro_expires": user[4].isoformat()
            })

# =============================
# 📌 ПРОВЕРКА СТАТУСА ПО ТОКЕНУ
# =============================
@app.route("/status", methods=["GET"])
def status():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Token не передан"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name, pro_expires FROM users WHERE token = %s", (token,))
            user = cur.fetchone()
            if not user:
                return jsonify({"error": "Пользователь не найден"}), 404

            return jsonify({
                "name": user[0],
                "pro_expires": user[1].isoformat()
            })

# --- Запуск приложения ---
if __name__ == "__main__":
    app.run(debug=True)