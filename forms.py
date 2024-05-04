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
    url_path = StringField(label="Unique URL path", description='Example: jordan-smith will have a url of seedcards.com/card/jordan-smith. This cannot be changed and must be unique from other accounts.', validators=[DataRequired()])
    name = StringField(label='Name', validators=[DataRequired()])
    job_title = StringField(label='Job Title', validators=[DataRequired()])
    submit = SubmitField(label="Submit")

#USE STRIPE
class PaymentForm(FlaskForm):
    credit_name = StringField(label='Name', validators=[DataRequired()])
    credit_email = StringField(label='Email', validators=[DataRequired(), validate_email])
    submit = SubmitField(label="Submit")

class LogInForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), validate_email])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log In")


class EditCardForm(FlaskForm):
    theme = SelectField(label="Theme", choices=[('Minimalist'), ('Artist'), ('Magazine'), ('Drama')])
    colors = SelectField(label="Colors", choices=[('Light'), ('Dark'), ('Soft')])
    name = StringField(label='Name')
    job_title = StringField(label='Job Title')
    headline_description = CKEditorField(label='Short Headline Description')
    displayed_email = StringField(label='Email displayed on card')
    phone = StringField(label="Phone")
    company = StringField(label='Company')
    location = StringField(label="Location")
    social_plat1 = SelectField(label="Social Platform 1", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link1 = StringField(label="Social Link 1")
    social_plat2 = SelectField(label="Social Platform 2", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link2 = StringField(label="Social Link 2")
    social_plat3 = SelectField(label="Social Platform 3", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link3 = StringField(label="Social Link 3")
    social_plat4 = SelectField(label="Social Platform 4", choices=[(''), ('Behance'), ('Discord'), ('Github'), ('Gitlab'), ('Instagram'), ('LinkedIn'), ('Mastodon'), ('Meta'), ('Pinterest'), ('Reddit'), ('Snapchat'), ('Threads'), ('TikTok'), ('Tumblr'), ('Twitch'), ('Twitter'), ('Twitter-X'), ('Youtube')])
    social_link4 = StringField(label="Social Link 4")
    website_link = StringField(label="Website")
    venmo = StringField(label="Venmo")
    stripe = StringField(label="Stripe")
    body = CKEditorField(label="Long Description")
    submit = SubmitField(label="Update")

class EditImagesForm(FlaskForm):
    profile_picture = FileField(label='Profile Picture')
    #logo = FileField(label='Logo')
    work1 = FileField(label='Work 1')
    work2 = FileField(label='Work 2')
    work3 = FileField(label='Work 3')
    work4 = FileField(label='Work 4')
    work5 = FileField(label='Work 5')
    submit = SubmitField(label="Update")


class EditAccountForm(FlaskForm):
    email = StringField(label='Account Email to log in', validators=[validate_email])
    password = PasswordField(label='Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
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
    
    