import random
import string
import smtplib
import os 

#TODO add to environment variables, get business email
my_email = "jackmail07@gmail.com"
password= "pmqxxxifsbshkyfr"

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
        
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, 
                            to_addrs= user.email,
                            msg=f"Seed Cards Temporary Password\n\n{content}")
        
    try:
        os.remove(f"{user.name}_email.txt")
    except OSError as e:
        # If it fails, inform the user.
        print("Error: %s - %s." % (e.filename, e.strerror))
    
    return temp_pass