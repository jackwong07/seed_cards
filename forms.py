from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, EqualTo, ValidationError
import re

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
    url_path = StringField(label="Unique URL path", validators=[DataRequired()])
    name = StringField(label='Name', validators=[DataRequired()])
    job_title = StringField(label='Job Title', validators=[DataRequired()])
    picture = FileField(label='Profile Picture (optional)')#need to edit this
    submit = SubmitField(label="Submit")

class PaymentForm(FlaskForm):
    credit_name = StringField(label='Name', validators=[DataRequired()])
    credit_email = StringField(label='Email', validators=[DataRequired(), validate_email])
    #credit_cardnum = StringField(label='Card Number', validators=[DataRequired()])
    #credit_expdate = StringField(label='Expiration Date', validators=[DataRequired()])
    #credit_cvv = StringField(label='CVV', validators=[DataRequired()])
    credit_zip = StringField(label='Zip', validators=[DataRequired()])
    submit = SubmitField(label="Submit")

class LogInForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), validate_email])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label="Log In")


class EditCardForm(FlaskForm):
    theme = SelectField(label="Theme", choices=[('artist'), ('corporate'), ('bold')])
    colors = SelectField(label="Colors", choices=[('dark'), ('light'), ('soft')])
    name = StringField(label='Name')
    job_title = StringField(label='Job Title')
    picture = FileField(label='Profile Picture')
    phone = StringField(label="Phone")
    logo = FileField(label='Logo')
    company = StringField(label='Company')
    location = StringField(label="Location")
    social_plat1 = SelectField(label="Social Platform 1", choices=[('Instagram'), ('Github'), ('DeviantArt')])
    social_link1 = StringField(label="Social Link 1")
    social_plat2 = SelectField(label="Social Platform 2", choices=[('Instagram'), ('Github'), ('DeviantArt')])
    social_link2 = StringField(label="Social Link 2")
    social_plat3 = SelectField(label="Social Platform 3", choices=[('Instagram'), ('Github'), ('DeviantArt')])
    social_link3 = StringField(label="Social Link 3")
    website_link = StringField(label="Website")
    venmo = StringField(label="Venmo")
    stripe = StringField(label="Stripe")
    submit = SubmitField(label="Update")

class EditAccountForm(FlaskForm):
    email = StringField(label='Email', validators=[validate_email])
    password = PasswordField(label='New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat New Password')
    url_path = StringField(label="Unique URL path", validators=[DataRequired()])
    submit = SubmitField(label="Update")