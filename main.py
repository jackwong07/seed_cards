from flask import Flask, jsonify, render_template, redirect, url_for, request, session, send_file, flash
import os
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import and_, Integer, String, Float, Boolean, Text, ForeignKey, desc
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import SignupForm, EditAccountForm, EditCardForm, PaymentForm, LogInForm, EditCardForm, VCard, EditImagesForm
from flask_ckeditor import CKEditor
from PIL import Image
import qrcode
import io
import base64
import boto3
from botocore.client import Config
import stripe
import json




#CREATE AND INITIALIZE FLASK APP
app = Flask(__name__, template_folder='templates')
#TODO: set as environment variable 
app.config['SECRET_KEY'] = "p$0s#9nfb0E48Q3W049*@B"
bootstrap = Bootstrap4(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

YOUR_DOMAIN = 'http://localhost:5000'


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
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    url_path: Mapped[str] = mapped_column(String(250), unique=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    theme: Mapped[str] = mapped_column(String(250), nullable=True)
    colors: Mapped[str] = mapped_column(String(250), nullable=True)    
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    job_title: Mapped[str] = mapped_column(String(250), nullable=True)
    profile_pic: Mapped[str] = mapped_column(String(250), nullable=True)
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
    work1: Mapped[str] = mapped_column(String(250), nullable=True)
    work2: Mapped[str] = mapped_column(String(250), nullable=True)
    work3: Mapped[str] = mapped_column(String(250), nullable=True)
    work4: Mapped[str] = mapped_column(String(250), nullable=True)
    work5: Mapped[str] = mapped_column(String(250), nullable=True)    
    body: Mapped[str] = mapped_column(Text, nullable=True)    
    payment: Mapped[bool] = mapped_column(Boolean, nullable=True)
    stripe_session_id: Mapped[str] = mapped_column(String(250), nullable=True, unique=True)
    #TODO make customer id and subscription id not unique
    stripe_customer_id: Mapped[str] = mapped_column(String(250), nullable=True, unique=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(250), nullable=True, unique=True)
    stripe_payment_status: Mapped[str] = mapped_column(String(250), nullable=True, unique=True)

    def __repr__(self):
        return f"<User {self.name}>"
    
    def get_id(self):
           return (self.id)


#create table schema in database
with app.app_context():
    db.create_all()


#FLASK LOGIN MANAGER AND INITIALIZATION
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# AWS S3 Bucket Initialization and Connection and save
aws_access_key_id = "AKIA6GBMF7OV5N6SKCW2"
aws_secret_access_key = "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"
BUCKET_NAME = "digibusiness-card-bucket"

s3 = boto3.client('s3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    config=Config(signature_version='s3v4'),
    region_name='us-east-2',
    endpoint_url='https://s3.us-east-2.amazonaws.com',
)

def save_to_s3(image, url_path, s3_name):
    img = Image.open(image)
    width, height= img.size
    if width>600:
        img.thumbnail((600,1080))
    buffer=io.BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"{url_path}_{s3_name}",
        Body=buffer)  


# STRIPE SETUP
stripe_keys = {
    "secret_key": "sk_test_51PB3m7FCnvuCuyrQiLhgCTOkCY1faz4U2hcxzJyzVDsBC669XuJg69nnvbNfFHnhe6KTXXbOdyyYrJxBZzx4173G00fcC9O1VM",
    "publishable_key": "pk_test_51PB3m7FCnvuCuyrQElzMQQT6F4nSdp94KTv773qyrcJlyVsG5nB7U4nUNM1N7FJEObJkgSLBMZQC5s5MFrCojOQb00pAkpEXhb",
    "price_id": "price_1PBK7IFCnvuCuyrQyzSzN2Fq",
    "endpoint_secret": "whsec_400ab6ec419190e2a8b0ebbed214579a0cda0285715cbc30046ec84fafbc41d6",
}
stripe.api_key = stripe_keys["secret_key"]


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
@app.route('/payment', methods=['GET','POST'])
def payment():
    url_path = current_user.url_path
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': stripe_keys["price_id"],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('payment_success', _external=True)+"?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for('home', _external=True),
            automatic_tax={'enabled': True},
        )
        #print("session: ", checkout_session.id, checkout_session.url, checkout_session)
        stripe_session_id = checkout_session.id
        current_user.stripe_session_id = stripe_session_id
        db.session.commit()
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    event = None
    payload = request.data
    
    try:
        event = json.loads(payload)
    except json.decoder.JSONDecodeError as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
    if stripe_keys["endpoint_secret"]:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, stripe_keys["endpoint_secret"]
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # HANDLE EVENTS
    if event and event['type'] == 'checkout.session.completed':
        customer_id = event['data']['object']['customer']
        subscription_id = event['data']['object']['subscription']
        session_id = event['data']['object']['id']
        payment_status = event['data']['object']['payment_status']
        if payment_status=="paid":
            print("Checkout complete, paid.")
            result = db.session.execute(db.select(User).where(and_(User.stripe_session_id==session_id, User.payment==False)))
            user = result.scalar()
            user.stripe_customer_id = customer_id
            user.stripe_subscription_id = subscription_id
            user.stripe_payment_status= payment_status
            db.session.commit()
        else:
            print("Checkout complete, not paid")
    if event['type']=="customer.subscription.deleted":
        cancelled_customer_id = event['data']['object']['customer']
        # cancelled_subscription_id = event['data']['object']['id']
        # cancelled_payment_status = event['data']['object']['status']        
        result = db.session.execute(db.select(User).where(and_(User.stripe_customer_id==cancelled_customer_id, User.payment==True)))
        user = result.scalar()
        # user.stripe_payment_status= cancelled_payment_status
        # user.payment=False
        db.session.delete(user)
        db.session.commit()
        print("Listened for account subscription deleted")
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)

@app.route('/payment-success')
def payment_success():
    #TODO: link to /card and pass current user    
    current_user.payment=True
    db.session.commit()
    flash(message="Payment Successful! Click Edit Card and Edit Images to customize your digital business card.")
    return redirect(url_for('card', url_path=current_user.url_path))




@app.route('/')
def home():
    session.pop('_flashes', None)
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
                email = request.form["email"].lower().strip(),
                password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8),
                url_path = request.form["url_path"].lower(),
                name = request.form["name"],
                job_title = request.form["job_title"],
                profile_pic = secure_filename(signup_form.picture.data.filename),
                payment=False,
                theme="magazine",
                colors="light",
                headline_description="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # UPLOAD PROFILE PIC TO S3
            profile_pic = signup_form.picture.data
            if profile_pic:
                s3_profile_pic = secure_filename(signup_form.picture.data.filename)
                url_path = request.form["url_path"].lower()
                save_to_s3(profile_pic, url_path, s3_profile_pic)
            

            login_user(new_user)

            return redirect(url_for('payment'))
    return render_template("register.html", signup_form=signup_form)




@app.route('/login', methods=["GET","POST"])
def login():
    login_form = LogInForm()
    session.pop('_flashes', None)
    if request.method=="POST" and login_form.validate_on_submit():
        form_email = request.form.get('email').lower().strip()
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


@app.route('/logout', methods=["GET","POST"])
def logout():
    url_path = current_user.url_path
    logout_user()
    return redirect(url_for('card', url_path=url_path))


@app.route('/card/<url_path>', methods=["GET","POST"])
def card(url_path):
    print(f"top of card {url_path}")
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    print(f"top of card {user}")
    if user:
        if user.payment==True:
            # GENERATE QR CODE
            print(f"inside if {user.payment}")
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
            # PROFILE PIC
            if user.profile_pic and user.profile_pic!="":
                profile_pic = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{user.profile_pic}"}, ExpiresIn=30)
            else:
                profile_pic = None
            
            # # WORKS
            if user.work1 and user.work1!="":
                work1_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{user.work1}"}, ExpiresIn=30)
            else:
                work1_url = None

            if user.work2 and user.work1!="":
                work2_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{user.work2}"}, ExpiresIn=30)
            else:
                work2_url = None
            
            if user.work3 and user.work1!="":
                work3_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{user.work3}"}, ExpiresIn=30)
            else:
                work3_url = None  
                
            if user.work4 and user.work1!="":
                work4_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{user.work4}"}, ExpiresIn=30)
            else:
                work4_url = None  
            
            if user.work5 and user.work1!="":
                work5_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{user.work5}"}, ExpiresIn=30)
            else:
                work5_url = None  
                
            # PASS CAN_EDIT FLAG TO SHOW MENU IF USER IS AUTHENTICATED
            if current_user.is_authenticated and current_user.url_path == user.url_path:
                can_edit=True
            else:
                can_edit=False
            return render_template("bus_card.html", user=user, can_edit=can_edit, qr_img=qr_encoded.decode('utf-8'), work1_url=work1_url, work2_url=work2_url, work3_url=work3_url, work4_url=work4_url, work5_url=work5_url, profile_pic=profile_pic)
    else:
        return render_template("no_user_found.html")


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
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    if current_user.is_authenticated and current_user.url_path == user.url_path:
        if request.method=="POST":
            current_user.email = request.form.get("email")
            current_user.url_path = request.form.get("url_path")
            db.session.commit()
            if request.form.get("password") != "":
                current_user.password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
                db.session.commit()
            return redirect(url_for('card', url_path=current_user.url_path))   
        return render_template("edit_account.html", user=current_user)


@app.route('/card/cancel-account/<url_path>', methods=["GET","POST"])
@login_required
def cancel_account(url_path):
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    
    # TODO DELETE S3 FILES
    if user.profile_pic:
        my_object = s3.Object(Bucket=BUCKET_NAME, Key=f"{url_path}_{user.profile_pic}")
        response = my_object.delete()
    
    if user.work1:
        s3.delete_object(Bucket=BUCKET_NAME, Key=f"{url_path}_{user.work1}")
    #s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{s3_work3_name}"}, ExpiresIn=30)


    # TODO DELETE USER FROM DATABASE, without getting 404 error after or set payment to false and payment status 
    stripe.Subscription.modify(
        user.stripe_subscription_id,
        cancel_at_period_end=True,
        )

    flash("Account cancelled. You will have access until the end of you bill month. Thank you for your support.")
    return redirect(url_for('home'))


@app.route('/card/edit-card/<url_path>', methods=["GET","POST"])
@login_required
def edit_card(url_path):
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    edit_card_form = EditCardForm() 
    # SHOW EXISTING DATA
    if current_user.is_authenticated and current_user.url_path == user.url_path:
        edit_card_form.theme.data = current_user.theme
        edit_card_form.colors.data = current_user.colors
        edit_card_form.name.data = current_user.name
        edit_card_form.job_title.data = current_user.job_title
        edit_card_form.headline_description.data = current_user.headline_description
        if not current_user.displayed_email:
            edit_card_form.displayed_email.data = current_user.email
        else:
            edit_card_form.displayed_email.data =current_user.displayed_email
        edit_card_form.phone.data = current_user.phone
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
        edit_card_form.body.data = current_user.body   
        
        
        # POPULATE WITH NEW DATA
        if request.method=="POST":   
            current_user.theme = edit_card_form.theme.data
            current_user.colors = edit_card_form.colors.data
            current_user.name = request.form.get('name')
            current_user.job_title = request.form.get('job_title')
            current_user.headline_description = request.form.get('headline_description')
            current_user.displayed_email = request.form.get('displayed_email')
            current_user.phone = request.form.get('phone')
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
            current_user.body = request.form.get('body')
            db.session.commit()
            return redirect(url_for('card', url_path=current_user.url_path))   
        return render_template("edit_card.html", user=current_user, edit_card_form=edit_card_form)

@app.route('/card/edit-images/<url_path>', methods=["GET","POST"])
@login_required
def edit_images(url_path):
    result = db.session.execute(db.select(User).where(User.url_path==url_path))
    user = result.scalar()
    # SHOW EXISTING DATA
    if current_user.is_authenticated and current_user.url_path == user.url_path:
        # SHOW EXISTING PROFILE PIC AND WORKS
        if current_user.profile_pic:
            profile_pic_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{current_user.profile_pic}"}, ExpiresIn=30)            
        else:
            profile_pic_url=None
                    
        if current_user.work1:
            work1_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{current_user.work1}"}, ExpiresIn=30)    
        else:
            work1_url=None
            
        if current_user.work2:
            work2_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{current_user.work2}"}, ExpiresIn=30)    
        else:
            work2_url=None

        if current_user.work3:
            work3_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{current_user.work3}"}, ExpiresIn=30)    
        else:
            work3_url=None
            
        if current_user.work4:
            work4_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{current_user.work4}"}, ExpiresIn=30)    
        else:
            work4_url=None
            
        if current_user.work5:
            work5_url = s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET_NAME, "Key": f"{url_path}_{current_user.work5}"}, ExpiresIn=30)    
        else:
            work5_url=None

        # UPDATE IMAGE TO S3 AND CHANGE DATABASE FILE NAMES
        if request.method=="POST":
            
            #PROFILE PICTURE
            if request.files["profile"]:
                profile_pic = request.files["profile"]
                s3_profile_pic = secure_filename(profile_pic.filename)
                save_to_s3(profile_pic, url_path, s3_profile_pic)     
                current_user.profile_pic = secure_filename(profile_pic.filename)
            
            #WORKS
            if request.files["work1"]:
                work1 = request.files["work1"]
                s3_work1 = secure_filename(work1.filename)
                save_to_s3(work1, url_path, s3_work1)     
                current_user.work1 = secure_filename(work1.filename)
  
            if request.files["work2"]:
                work2 = request.files["work2"]
                s3_work2 = secure_filename(work2.filename)
                save_to_s3(work2, url_path, s3_work2)     
                current_user.work2 = secure_filename(work2.filename)
                
            if request.files["work3"]:
                work3 = request.files["work3"]
                s3_work3 = secure_filename(work3.filename)
                save_to_s3(work3, url_path, s3_work3)     
                current_user.work3 = secure_filename(work3.filename)
 
            if request.files["work4"]:
                work4 = request.files["work4"]
                s3_work4 = secure_filename(work4.filename)
                save_to_s3(work4, url_path, s3_work4)     
                current_user.work4 = secure_filename(work4.filename)


            if request.files["work5"]:
                work5 = request.files["work5"]
                s3_work5 = secure_filename(work5.filename)
                save_to_s3(work5, url_path, s3_work5)     
                current_user.work5 = secure_filename(work5.filename)
            
            db.session.commit()
            return redirect(url_for('card', url_path=current_user.url_path))  
    return render_template("edit_images.html", user=current_user,  profile_pic_url=profile_pic_url, work1_url=work1_url, work2_url=work2_url,  work3_url=work3_url,  work4_url=work4_url, work5_url=work5_url)  

if __name__ == "__main__":
    app.run(debug=True)
