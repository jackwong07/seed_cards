from flask import Flask, render_template, redirect, url_for, request, session, jsonify, flash
import os
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, Text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import SignupForm, EditAccountForm, EditCardForm, PaymentForm, LogInForm, EditCardForm
from flask_ckeditor import CKEditor


#CREATE AND INITIALIZE FLASK APP
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = "p$0s#9nfb0E48Q3W049*@B"
bootstrap = Bootstrap4(app)

#CREATE DATABASE
class Base(DeclarativeBase):
    pass
#configure sQLite database, relative to the app instance folder
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///business-cards.db" 
#create the extension
db = SQLAlchemy(model_class=Base)
# initialize the app with the extension
db.init_app(app)

ckeditor = CKEditor(app)

#CREATE TABLE IN DB
#define a model class to generate a table name
class User(db.Model, UserMixin):
    url_path: Mapped[str] = mapped_column(String(250), primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    job_title: Mapped[str] = mapped_column(String(250), nullable=True)
    provided_profile_pic: Mapped[str] = mapped_column(String(250), nullable=True)
    s3_profile_pic: Mapped[str] = mapped_column(String(250), nullable=True)
    headline_description: Mapped[str] = mapped_column(Text, nullable=True)
    displayed_email: Mapped[str] = mapped_column(String(250), nullable=True)
    phone: Mapped[str] = mapped_column(String(250), nullable=True)
    logo: Mapped[str] = mapped_column(String(250), nullable=True)
    company: Mapped[str] = mapped_column(String(250), nullable=True)
    location: Mapped[str] = mapped_column(String(250), nullable=True)
    social_plat1: Mapped[str] = mapped_column(String(250), nullable=True)
    social_link1: Mapped[str] = mapped_column(String(250), nullable=True)
    social_plat2: Mapped[str] = mapped_column(String(250), nullable=True)
    social_link2: Mapped[str] = mapped_column(String(250), nullable=True)
    social_plat3: Mapped[str] = mapped_column(String(250), nullable=True)
    social_link3: Mapped[str] = mapped_column(String(250), nullable=True)
    social_plat4: Mapped[str] = mapped_column(String(250), nullable=True)
    social_link4: Mapped[str] = mapped_column(String(250), nullable=True)
    website_link: Mapped[str] = mapped_column(String(250), nullable=True)
    venmo: Mapped[str] = mapped_column(String(250), nullable=True)
    stripe: Mapped[str] = mapped_column(String(250), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=True)    
    payment: Mapped[bool] = mapped_column(Boolean, nullable=True)

    def __repr__(self):
        return f"<User {self.name}>"
    
    def get_id(self):
           return (self.url_path)

#create table schema in database
with app.app_context():
    db.create_all()


#FLASK LOGIN MANAGER AND INITIALIZATION
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



# CREATE ROUTES AND RENDER HTML TEMPLATES
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=["GET","POST"])
def register():
    signup_form = SignupForm()
    if request.method=="POST" and signup_form.validate_on_submit():
        form_email = request.form['email']
        result = db.session.execute(db.select(User).where(User.email==form_email))
        user = result.scalar()
        if user:
            #if user already exists
            flash("You already have an account with this email. Please log in.")
            return redirect(url_for('login'))
        else:
            new_user = User(
                email = request.form["email"],
                password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8),
                url_path = request.form["url_path"].lower(),
                name = request.form["name"],
                job_title = request.form["job_title"],
                payment=False,
            )
            db.session.add(new_user)
            db.session.commit()
            session['user_email']=request.form["email"]
            return redirect(url_for('payment'))
    return render_template("register.html", signup_form=signup_form)


@app.route('/payment', methods=["GET","POST"])
def payment():
    payment_form = PaymentForm()
    if payment_form.validate_on_submit():
        session_email = session['user_email']
        result = db.session.execute(db.select(User).where(User.email==session_email))
        user = result.scalar()
        login_user(user)
        current_user.payment = True
        db.session.commit()
        # new_payment = User(
        #                   name = signup_form.name.data,
        #                   email = signup_form.email.data,
        #                   job_title = signup_form.job_title.data,
        #                 )
        return redirect(url_for('card', url_path=current_user.url_path))
    return render_template("payment_form.html", payment_form=payment_form)


@app.route('/login', methods=["GET","POST"])
def login():
    login_form = LogInForm()
    session.pop('_flashes', None)
    if request.method=="POST":
        form_email = request.form.get('email')
        form_password = request.form.get('password')
        result = db.session.execute(db.select(User).where(User.email == form_email))
        user = result.scalar()
        if user:
            if check_password_hash(user.password, form_password):
                login_user(user)
                flash("Logged in successfully")
                return redirect(url_for('card', url_path=current_user.url_path))            
            else:
                flash("Password is incorrect")
        else:
            flash("Email not found")
            return render_template("login.html", login_form=login_form)
    return render_template("login.html", login_form=login_form)



@app.route('/card/<url_path>', methods=["GET","POST"])
def card(url_path):
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    if user.payment ==True:
        if current_user.is_authenticated and current_user.url_path == user.url_path:
            can_edit=True
            print("authenticated")
            #show edit button
            return render_template("bus_card.html", user=user, can_edit=can_edit)
        return render_template("bus_card.html", user=user)
    else:
        return "Sorry, user doesn't exist"


# EDIT ROUTES - USER MUST BE LOGGED IN
@app.route('/card/edit-account/<url_path>', methods=["GET","POST"])
@login_required
def edit_account(url_path):
    edit_account_form = EditAccountForm()
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    if current_user.is_authenticated and current_user.url_path == user.url_path:
        edit_account_form.email.data = current_user.email
        edit_account_form.url_path.data = current_user.url_path
        return render_template("edit_account.html", user=current_user, edit_account_form=edit_account_form)

@app.route('/card/edit-card/<url_path>', methods=["GET","POST"])
@login_required
def edit_card(url_path):
    edit_card_form = EditCardForm()
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    
    # Show existing data
    if current_user.is_authenticated and current_user.url_path == user.url_path:
        edit_card_form.name.data = current_user.name
        edit_card_form.job_title.data = current_user.job_title
        if not user.displayed_email:
            edit_card_form.displayed_email.data = current_user.email
        else:
            edit_card_form.displayed_email.data =user.displayed_email
        return render_template("edit_card.html", user=current_user, edit_card_form=edit_card_form)


if __name__ == "__main__":
    app.run(debug=True)
