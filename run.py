# run.py
from flask import Flask
from app.models import db
from app.routes import routes
import os


app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = os.getenv("FLASK_SECRET", "supersecretkey")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(routes)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
