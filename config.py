import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "svl_secret_2025")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ayushqriocity_db_user:TZeelwski4lX0xvK@cluster0.fb6gvp7.mongodb.net/smart_virtual_lab?appName=Cluster0")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAtqGXv9KDV5TzFbLTcygRR73hxU5P5ZmI")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    DB_NAME = "smart_virtual_lab"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024