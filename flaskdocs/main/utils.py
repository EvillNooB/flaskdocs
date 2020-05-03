from flaskdocs import mail
from flask_mail import Message


def send_email_to_staff(staff, document, daysleft):
    msg = Message(f'Уведомление о документе - {document.name}', sender="kahrali.hvss@sas.ke", recipients=[staff.email])
    msg.body = f'''{staff.first_name} {staff.second_name}, Ваш {document.name} истекает {document.expiration_date.format("DD.MM.YYYY")}
Осталось дней {daysleft} 


'''
    mail.send(msg)


def send_email_to_group(group, daysleft, document, staff):
    receivers = []
    for user in group.user_count:
        if user.use_email:
            receivers.append(user.email)
    msg = Message(f'Уведомление о документе - {document.name}', sender="kahrali.hvss@sas.ke", recipients=receivers)
    msg.body = f'''Документ '{document.name}'' который принадлежит работнику - {staff.first_name} {staff.second_name} 
    Истекает {document.expiration_date.format("DD.MM.YYYY")}
Осталось дней {daysleft} 

Контакты работника:
Телефон {staff.phone.e164}
Email {staff.email}

'''
    if receivers:
        mail.send(msg)

def send_sms_to_staff():
    pass

def send_sms_to_group():
    pass
