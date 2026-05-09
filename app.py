import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    subscribed_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inscription', methods=['POST'])
def inscription():
    email = request.form.get('email', '').strip().lower()
    if not email or '@' not in email or '.' not in email:
        return '', 400
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO subscribers (email) VALUES (%s) ON CONFLICT (email) DO NOTHING", (email,))
                conn.commit()
        return '', 200
    except Exception as e:
        print(e)
        return '', 500

@app.route('/admin')
def admin():
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC")
                subscribers = cur.fetchall()
        count = len(subscribers)
        return f"""
        <html><body style="font-family:sans-serif;padding:2rem;">
        <h1>📊 Inscrits TAWURI</h1>
        <p><strong>{count}</strong> inscrit(s)</p>
        <ul>{"".join(f'<li>{s["email"]} – {s["subscribed_at"].strftime("%d/%m/%Y %H:%M")}</li>' for s in subscribers)}</ul>
        </body></html>
        """
    except Exception as e:
        return f"Erreur : {e}", 500

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))