import random
import string
import smtplib
import os 

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail





#TODO add to environment variables, get business email
my_email = os.environ.get("MY_EMAIL")
password= os.environ.get("MY_EMAIL_PASSWORD")

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
    
    with open(f"{user.name}_email.txt", mode='w') as send_email:
        send_email.write(content)
        
    message = Mail(
        from_email='rae.a.warner@gmail.com',
        to_emails=user.email,
        subject=f'Hi {user.name}, welcome to Seed Cards!',
        html_content=f'{content}')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e.message)

    return temp_pass
    # with smtplib.SMTP("smtp.gmail.com") as connection:
    #     connection.starttls()
    #     connection.login(user=my_email, password=password)
    #     connection.sendmail(from_addr=my_email, 
    #                         to_addrs= user.email,
    #                         msg=f"Seed Cards Temporary Password\n\n{content}")
        
    # try:
    #     os.remove(f"{user.name}_email.txt")
    # except OSError as e:
    #     # If it fails, inform the user.
    #     print("Error: %s - %s." % (e.filename, e.strerror))
    
    # return temp_pass


# SEND EMAIL FOR REGISTRATION
def email_registration_success(user):
    with open(f"emails/registration_success.txt", mode='r') as template:
        content = template.read()
        content = content.replace("[NAME]", user.name)
        content = content.replace("[EMAIL]", user.email)
        content = content.replace("[URL_PATH]", user.url_path)
    
    with open(f"{user.name}_registration_email.txt", mode='w') as send_email:
        send_email.write(content)
        
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, 
                            to_addrs= user.email,
                            msg=f"Seed Cards Registration Complete\n\n{content}")
        
    try:
        os.remove(f"{user.name}_registration_email.txt")
    except OSError as e:
        # If it fails, inform the user.
        print("Error: %s - %s." % (e.filename, e.strerror))
        
        
# SEND EMAIL FOR CANCELLATION
def email_cancellation_success(user):
    with open(f"emails/cancellation_success.txt", mode='r') as template:
        content = template.read()
        content = content.replace("[NAME]", user.name)
        content = content.replace("[URL_PATH]", user.url_path)

    
    with open(f"{user.name}_cancellation_email.txt", mode='w') as send_email:
        send_email.write(content)
        
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, 
                            to_addrs= user.email,
                            msg=f"Seed Cards Cancellation Complete\n\n{content}")
        
    try:
        os.remove(f"{user.name}_cancellation_email.txt")
    except OSError as e:
        # If it fails, inform the user.
        print("Error: %s - %s." % (e.filename, e.strerror))
        
        
def email_contact_form(contact_name, contact_email, contact_message):       
    contact_name = contact_name
    contact_email = contact_email
    contact_message = contact_message
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, 
                            to_addrs= my_email,
                            msg=f"Seed Cards New Contact Message\n\nName: {contact_name}\nEmail: {contact_email}\nMessage: {contact_message}")