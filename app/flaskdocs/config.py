import os 
import json

script_dir = os.path.dirname(__file__)
rel_path = "config.json"
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path) as config_file:
    config = json.load(config_file)

class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_ENGINE_OPTIONS: {
        "POOL_PRE_PING": True,
        "POOL_RECYCLE": 250,
    }
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_RECYCLE = 250
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    MAIL_USERNAME = config.get('MAIL_USERNAME')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD')
    TWILIO_AUTH_SID = config.get('TWILIO_AUTH_SID')
    TWILIO_AUTH_TOKEN = config.get('TWILIO_AUTH_TOKEN')
    GOOGLE_CLIENT_ID = config.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = config.get('GOOGLE_CLIENT_SECRET')

    TWILIO_FROM = config.get('TWILIO_FROM')
    SQLALCHEMY_TRACK_MODIFICATIONS = config.get('SQLALCHEMY_TRACK_MODIFICATIONS')
    MAIL_SERVER = config.get('MAIL_SERVER')
    MAIL_PORT = config.get('MAIL_PORT')
    MAIL_USE_SSL = config.get('MAIL_USE_SSL')
    GOOGLE_DISCOVERY_URL = config.get('GOOGLE_DISCOVERY_URL')
    