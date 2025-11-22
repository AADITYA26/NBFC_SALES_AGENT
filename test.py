from flask import Flask
from app.models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")

    user = User(username="aadi", password=generate_password_hash("pass123"))
    db.session.add(user)
    db.session.commit()
    print("✅ User 'aadi' added successfully!")