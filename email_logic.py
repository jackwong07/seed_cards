import random
import string
import smtplib
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



# SEND EMAIL FOR FORGOT PASSWORD FLOW, SENDING TEMPORARY PASSWORD
def email_temp_password(user):
    temp_pass = ''.join(random.choices(string.ascii_uppercase + 
                                 string.digits, k=8))
    with open(f"emails/temp_password.txt", mode='r') as template:
        content = template.read()
        content = content.replace("[NAME]", user.name)
        content = content.replace("[EMAIL]", user.email)
        content = content.replace("[URL_PATH]", user.url_path)
        content = content.replace("[TEMPORARY_PASSWORD]", temp_pass)

    message = Mail(
        from_email='rae.a.warner@gmail.com',
        to_emails=user.email,
        subject=f'Hi {user.name}, your new password requeest',
        html_content=f'{content}')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        mail_json = message.get()
        response = sg.client.mail.send.post(request_body=mail_json)

        print(response.status_code)
        print(response.headers)
    except Exception as e:
        print(e.message)
    return temp_pass





# SEND EMAIL FOR REGISTRATION
def email_registration_success(user):
    with open(f"emails/registration_success.txt", mode='r') as template:
        content = template.read()
        content = content.replace("[NAME]", user.name)
        content = content.replace("[EMAIL]", user.email)
        content = content.replace("[URL_PATH]", user.url_path)

    message = Mail(
        from_email='rae.a.warner@gmail.com',
        to_emails=user.email,
        subject=f'Hi {user.name}, welcome to Seed Cards!',
        html_content=f'{content}')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        mail_json = message.get()
        response = sg.client.mail.send.post(request_body=mail_json)

        print(response.status_code)
        print(response.headers)
    except Exception as e:
        print(e.message)



# SEND EMAIL FOR CANCELLATION
def email_cancellation_success(user):
    with open(f"emails/cancellation_success.txt", mode='r') as template:
        content = template.read()
        content = content.replace("[NAME]", user.name)
        content = content.replace("[URL_PATH]", user.url_path)
    
    message = Mail(
        from_email='rae.a.warner@gmail.com',
        to_emails=user.email,
        subject=f'Cancel card complete for {user.name}',
        html_content=f'{content}')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        mail_json = message.get()
        response = sg.client.mail.send.post(request_body=mail_json)

        print(response.status_code)
        print(response.headers)
    except Exception as e:
        print(e.message)


def email_contact_form(contact_name, contact_email, contact_message):       
    contact_name = contact_name
    contact_email = contact_email
    contact_message = contact_message
    
    message = Mail(
        from_email='rae.a.warner@gmail.com',
        to_emails='rae.a.warner@gmail.com',
        subject=f'Contact form for {contact_email}',
        html_content=f'Name: {contact_name}\nEmail: {contact_email}\nMessage: {contact_message}')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        mail_json = message.get()
        response = sg.client.mail.send.post(request_body=mail_json)

        print(response.status_code)
        print(response.headers)
    except Exception as e:
        print(e.message)