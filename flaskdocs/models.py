from datetime import datetime
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskdocs import db, login_manager, app
from flask_login import UserMixin
# import sqlalchemy_utils
from sqlalchemy_utils import force_auto_coercion, PasswordType, EmailType, PhoneNumberType, ArrowType, JSONType
import arrow, phonenumbers, passlib
force_auto_coercion()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(20), unique=True, nullable=False)
    email = db.Column(EmailType(), unique=True, nullable=False)
    phone = db.Column(PhoneNumberType(), unique=True, nullable=False)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), unique=False, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')

    # @staticmethod  
    # def verify_reset_token(token):
    #     s = Serializer(app.config['SECRET_KEY'])
    #     try:
    #         user_id = s.loads(token)['user_id']
    #     except:
    #         return None
    #     return User.query.get(user_id)

    def __repr__(self):
        return f" Пользователь ('{self.username}', '{self.email}','{self.phone.international}')"


# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.Unicode(100), nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     content = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

#     def __repr__(self):
#         return f"Post('{self.title}', '{self.date_posted}')"

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    second_name = db.Column(db.Unicode(100), unique=False, nullable=False)
    first_name = db.Column(db.Unicode(100), unique=False, nullable=False)
    email = db.Column(EmailType(), unique=True, nullable=False)
    phone = db.Column(PhoneNumberType(), unique=True, nullable=False)
    documents = db.relationship('Documents', backref='owner', lazy=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    def __repr__(self):
        return f"Работник('{self.first_name}', '{self.second_name}','{self.phone.international}')"

class Documents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(20), unique=False, nullable=False)
    expiration_date = db.Column(ArrowType(), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    notifications = db.Column(JSONType)

    def __repr__(self):
        return f"Документ('{self.name}', Действителен до '{self.expiration_date}')"

class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(40), unique=True, nullable=False)
    user_count = db.relationship('User', backref='group', lazy=True)
    staff_count = db.relationship('Staff', backref='group', lazy=True)

    def __repr__(self):
        return f"Группа - '{self.name}'"

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first = db.Column(db.Integer, unique=False, nullable=False, default=20)
    second = db.Column(db.Integer, unique=False, nullable=False, default=15)
    third = db.Column(db.Integer, unique=False, nullable=False, default=10)
 
