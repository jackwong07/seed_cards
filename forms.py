from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, EqualTo, ValidationError
import re
from flask_ckeditor import CKEditorField

#FORM VALIDATION AND CREATION
def validate_email(form, field):
    if len(field.data) < 8:
        raise ValidationError("Email must be at least 8 characters")
    elif "@" not in field.data or "." not in field.data:
        raise ValidationError("Must contain @ and . in the email")

def validate_url_path(form, field):
    url_regex = re.compile(r'^[^<>!@#$%^&*()_+={}\[\]:;,.?/~`]+$')
    if not url_regex.match(field.data):
        raise ValidationError("URL path cannot contain certain symbols. Try to only use characters, numbers, and dashes. Example: 'john-smith'")

class SignupForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), validate_email])
    password = PasswordField(label='Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    url_path = StringField(label="Unique URL path", description='Example: jordan-smith will have a url of https://seed-cards.onrender.com/card/jordan-smith. This cannot be changed and must be unique from other accounts.', validators=[DataRequired()])
    name = StringField(label='Name', validators=[DataRequired()])
    job_title = StringField(label='Job Title', validators=[DataRequired()])
    submit = SubmitField(label="Submit")



class LogInForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), validate_email])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log In")


class EditCardForm(FlaskForm):
    theme = SelectField(label="Choose your theme", choices=[('Magazine'), ('Minimalist'), ('Drama')])
    name = StringField(label='Name')
    job_title = StringField(label='Job title')
    headline_description = CKEditorField(label='Short headline description')
    displayed_email = StringField(label='Email displayed on card')
    phone = StringField(label="Phone number")
    company = StringField(label='Company')
    location = StringField(label="Location (example: Brooklyn, NY)")
    social_plat1 = SelectField(label="Choose your social platform 1 (example: Instagram)", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link1 = StringField(label="Social link 1 (example: www.instagram.com/user_name)")
    social_plat2 = SelectField(label="Choose your social platform 2 (example: LinkedIn)", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link2 = StringField(label="Social link 2 (example: https://www.linkedin.com/in/user-name-id/)")
    social_plat3 = SelectField(label="Choose your social platform 3", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link3 = StringField(label="Social link 3")
    social_plat4 = SelectField(label="Choose your social platform 4", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link4 = StringField(label="Social link 4")
    website_link = StringField(label="Website")
    venmo = StringField(label="Venmo")
    stripe = StringField(label="Stripe")
    body = CKEditorField(label="Long Description")
    submit = SubmitField(label="Update")


class EditPasswordForm(FlaskForm):
    confirm  = PasswordField('Repeat New Password')
    submit = SubmitField(label="Update")

class ForgotPasswordForm(FlaskForm):
    email = StringField(label='Email', validators=[validate_email])
    url_path = StringField(label="URL path")
    submit = SubmitField(label="Email Temp Password")

# SEND CONTACT INFO as VCF
class VCard():
    def __init__(self, display_name, job_title, company, email, phone, address):
        self.display_name = display_name
        self.job_title = job_title
        self.company = company
        self.email = email
        self.phone = phone
        self.address = address
    
    