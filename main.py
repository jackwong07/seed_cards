from flask import Flask, render_template, redirect, url_for, request, session, send_file, flash
import os
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, Text
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import SignupForm, EditAccountForm, EditCardForm, PaymentForm, LogInForm, EditCardForm, VCard
from flask_ckeditor import CKEditor
from PIL import Image
import qrcode
import io
import base64
import boto3
from botocore.client import Config




#CREATE AND INITIALIZE FLASK APP
app = Flask(__name__, template_folder='templates')
#TODO: set as environment variable 
app.config['SECRET_KEY'] = "p$0s#9nfb0E48Q3W049*@B"
bootstrap = Bootstrap4(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


#CREATE DATABASE
class Base(DeclarativeBase):
    pass
#configure sQLite database, relative to the app instance folder
#TODO: set as environment variable 
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
    #TODO: theme: Mapped[str] = mapped_column(String(250), nullable=True)
    # colors: Mapped[str] = mapped_column(String(250), nullable=True)    
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
    #TODO: work1: Mapped[str] = mapped_column(String(250), nullable=True)
    # work2: Mapped[str] = mapped_column(String(250), nullable=True)
    # work3: Mapped[str] = mapped_column(String(250), nullable=True)
    # work4: Mapped[str] = mapped_column(String(250), nullable=True)
    # work5: Mapped[str] = mapped_column(String(250), nullable=True)    
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


# AWS S3 Bucket Initialization and Connection
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = "digibusiness-card-bucket"

s3 = boto3.client('s3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    config=Config(signature_version='s3v4'),
    region_name='us-east-2',
    endpoint_url='https://s3.us-east-2.amazonaws.com',
)


#GENERATE VCF FILE TO SAVE CONTACTS
def get_vcard(vcard: VCard) -> io.BytesIO:
    # Render the vcard template with the user's data,
    with app.app_context():
        content = render_template('template.vcf.jinja2', **vcard.__dict__)
    # Remove all the extra lines that jinja2 leaves in there. (ugh.)
    content = '\n'.join(filter(lambda line: bool(line.strip()), content.split('\n')))
    # Create a file-like object to send to the client
    file_ = io.BytesIO()
    file_.write(content.encode('UTF-8'))
    file_.seek(0)

    return file_




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
                theme="minimalist",
                colors="light",
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
    if request.method=="POST" and login_form.validate_on_submit():
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

        # GENERATE QR CODE
        qr = qrcode.QRCode(version=3, box_size=5, border=5, error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr_link = f"http://127.0.0.1:5000/card/{url_path}"
        qr.add_data(qr_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        buffer.seek(0)
        buffer.truncate(0)
        qr_img.save(buffer, format="png")
        qr_encoded = base64.b64encode(buffer.getvalue())
        
        # GRAB IMAGES FROM S3
        #TODO: edit key path to dynamic user.s3_work_names
        work1_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_abstract.jpg"}, ExpiresIn=30)
        work2_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_chairs.jpg"}, ExpiresIn=30)
        work3_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_city.jpg"}, ExpiresIn=30)
        work4_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_forest_background.jpg"}, ExpiresIn=30)
        work5_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_mobile_background.jpeg"}, ExpiresIn=30)

        # PASS CAN_EDIT FLAG TO SHOW MENU IF USER IS AUTHENTICATED
        if current_user.is_authenticated and current_user.url_path == user.url_path:
            can_edit=True
            return render_template("bus_card.html", user=user, can_edit=can_edit, qr_img=qr_encoded.decode('utf-8'), work1_url=work1_url, work2_url=work2_url, work3_url=work3_url, work4_url=work4_url, work5_url=work5_url)
        return render_template("bus_card.html", user=user, qr_img=qr_encoded.decode('utf-8'), work1_url=work1_url, work2_url=work2_url, work3_url=work3_url, work4_url=work4_url, work5_url=work5_url)
    else:
        return "Sorry, user doesn't exist"


@app.route("/vcard/download/<url_path>")
def generate_vcf(url_path):
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    user_vcard = VCard(
        display_name = user.name,
        job_title = user.job_title,
        company = user.company,
        email = user.displayed_email,
        address = user.location,
        phone = user.phone
        ) 
    return send_file(get_vcard(user_vcard), mimetype='text/vcard')

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
        # edit_card_form.theme.data = current_user.theme
        # edit_card_form.colors.data = current_user.colors
        edit_card_form.name.data = current_user.name
        edit_card_form.job_title.data = current_user.job_title
        edit_card_form.profile_picture.data = current_user.provided_profile_pic
        edit_card_form.headline_description.data = current_user.headline_description
        if not user.displayed_email:
            edit_card_form.displayed_email.data = current_user.email
        else:
            edit_card_form.displayed_email.data =user.displayed_email
        edit_card_form.phone.data = current_user.phone
        edit_card_form.logo.data = current_user.logo
        edit_card_form.company.data = current_user.company
        edit_card_form.location.data = current_user.location
        edit_card_form.social_plat1.data = current_user.social_plat1
        edit_card_form.social_plat2.data = current_user.social_plat2
        edit_card_form.social_plat3.data = current_user.social_plat3
        edit_card_form.social_plat4.data = current_user.social_plat4
        edit_card_form.social_link1.data = current_user.social_link1
        edit_card_form.social_link2.data = current_user.social_link2
        edit_card_form.social_link3.data = current_user.social_link3
        edit_card_form.social_link4.data = current_user.social_link4                
        edit_card_form.website_link.data = current_user.website_link
        edit_card_form.venmo.data = current_user.venmo
        edit_card_form.stripe.data = current_user.stripe
        # TODO: edit_card_form.work1.data = current_user.work1       
        edit_card_form.body.data = current_user.body
        
        if request.method=="POST":
            work1 = edit_card_form.work1.data
            work2 = edit_card_form.work2.data
            work3 = edit_card_form.work3.data
            work4 = edit_card_form.work4.data
            work5 = edit_card_form.work5.data
            # TODO: Save these to database
            work1_name=work1.filename
            work2_name=work2.filename
            work3_name=work3.filename
            work4_name=work4.filename
            work5_name=work5.filename
            #TODO: save these as AWS S3 filenames
            s3_work1_name = secure_filename(work1_name)
            s3_work2_name = secure_filename(work2_name)
            s3_work3_name = secure_filename(work3_name)
            s3_work4_name = secure_filename(work4_name)
            s3_work5_name = secure_filename(work5_name)

            work_dictionary ={
                s3_work1_name: work1,
                s3_work2_name: work2,
                s3_work3_name: work3,
                s3_work4_name: work4,
                s3_work5_name: work5,
            }
            
            for s3_work_name, work in work_dictionary.items():
                img = Image.open(work)
                width, height= img.size
                if width>600:
                    img.thumbnail((600,1080))
                buffer=io.BytesIO()
                img.save(buffer, format="JPEG")
                buffer.seek(0)
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=f"{url_path}_{s3_work_name}",
                    Body=buffer)
                        
            
            # current_user.theme = edit_card_form.theme.data
            # current_user.colors = edit_card_form.colors.data
            current_user.name = request.form.get('name')
            current_user.job_title = request.form.get('job_title')
            current_user.provided_profile_pic = request.form.get('provided_profile_pic')
            current_user.headline_description = request.form.get('headline_description')
            user.displayed_email = request.form.get('displayed_email')
            current_user.phone = request.form.get('phone')
            current_user.logo = request.form.get('logo')
            current_user.company = request.form.get('company')
            current_user.location = request.form.get('location')
            current_user.social_plat1 = request.form.get('social_plat1')
            current_user.social_plat2 = request.form.get('social_plat2')
            current_user.social_plat3 = request.form.get('social_plat3')
            current_user.social_plat4 = request.form.get('social_plat4')
            current_user.social_link1 = request.form.get('social_link1')
            current_user.social_link2 = request.form.get('social_link2')
            current_user.social_link3 = request.form.get('social_link3')
            current_user.social_link4  = request.form.get('social_link4')             
            current_user.website_link = request.form.get('website_link')
            current_user.venmo = request.form.get('venmo')
            current_user.stripe = request.form.get('stripe')
            # TODO: current_user.work1 = work1_name 
            # TODO: current_user.s3_work1 = s3_work1_name
            current_user.body = request.form.get('body')
            db.session.commit()
            return redirect(url_for('card', url_path=current_user.url_path))   
        return render_template("edit_card.html", user=current_user, edit_card_form=edit_card_form)


if __name__ == "__main__":
    app.run(debug=True)
