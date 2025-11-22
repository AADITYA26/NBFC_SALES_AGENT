# app/routes.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Chat
from main_orchestrator import LoanMasterAgent
import os, json

routes = Blueprint('routes', __name__)
agent = LoanMasterAgent(api_key=os.getenv("GEMINI_API_KEY"))

@routes.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('routes.chat'))
    return redirect(url_for('routes.login'))

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('routes.chat'))
        return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

@routes.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    if User.query.filter_by(username=username).first():
        return render_template('login.html', error="User already exists.")
    hashed_pw = generate_password_hash(password)
    user = User(username=username, password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('routes.login'))

@routes.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    return render_template('chat.html')

@routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.login'))

@routes.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 403

    data = request.json
    message = data.get("message", "")

    # Save user message
    chat = Chat(user_id=session['user_id'], role="user", message=message)
    db.session.add(chat)
    db.session.commit()

    # Get response from LoanMasterAgent
    response = agent.process_message(message)

    # Save agent message
    chat_response = Chat(user_id=session['user_id'], role="agent", message=response)
    db.session.add(chat_response)
    db.session.commit()

    return jsonify({"response": response})
@routes.route('/get_history')
def get_history():
    if 'user_id' not in session:
        return jsonify({"history": []})
    chats = Chat.query.filter_by(user_id=session['user_id']).order_by(Chat.id).all()
    history = [{"role": c.role, "message": c.message} for c in chats]
    return jsonify({"history": history})