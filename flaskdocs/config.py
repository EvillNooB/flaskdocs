import os 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    TWILIO_AUTH_SID = os.environ.get('ACCOUNT_SSID')
    TWILIO_AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
    TWILIO_FROM = '+12057518009'