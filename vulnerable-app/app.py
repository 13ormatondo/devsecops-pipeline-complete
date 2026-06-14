from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')

# Vulnérabilité XSS
@app.route('/')
def home():
    name = request.args.get('name', 'Guest')
    return render_template_string(f"<h1>Welcome {name}!</h1><p>Enter your data below.</p>")

# Vulnérabilité SQL Injection
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"status": "success", "message": f"Welcome {user[1]}", "role": user[3]})
    return jsonify({"error": "Invalid credentials"}), 401

# Vulnérabilité Command Injection
@app.route('/ping')
def ping():
    ip = request.args.get('ip', '127.0.0.1')
    result = subprocess.check_output(f"ping -c 1 {ip}", shell=True, stderr=subprocess.STDOUT)
    return result.decode('utf-8')

# Vulnérabilité IDOR (Insecure Direct Object Reference)
@app.route('/user/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "username": user.username, "role": user.role})
    return jsonify({"error": "User not found"}), 404

# Initialisation de la base de données
@app.route('/init-db')
def init_db():
    db.create_all()
    admin = User(username='admin', password='admin123', role='admin')
    alice = User(username='alice', password='alice123', role='user')
    bob = User(username='bob', password='bob123', role='user')
    db.session.add_all([admin, alice, bob])
    db.session.commit()
    return "Database initialized with admin, alice, bob!"

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
