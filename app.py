from flask import Flask
from config import Config
from extensions import mongo
from routes.auth import auth_bp
from routes.student import student_bp
from routes.faculty import faculty_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["MONGO_URI"] = Config.MONGO_URI

    mongo.init_app(app)

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)