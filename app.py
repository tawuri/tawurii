import os
from flask import Flask, render_template, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

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
    except Exception:
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
        return f"Erreur DB : {e}", 500
