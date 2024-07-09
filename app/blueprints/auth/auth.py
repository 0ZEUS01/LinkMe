from flask_mail import Message
import os
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import bcrypt
import time
from flask import Flask, jsonify, render_template, redirect, url_for, flash, session, current_app, request
from flask import Blueprint
from .forms import NewPasswordForm, RecoverPasswordForm, SignupForm, SigninForm, VerifyCodeForm
from werkzeug.utils import secure_filename
import MySQLdb.cursors
from app import mail, mysql 

auth_blueprint = Blueprint('auth_blueprint', __name__, static_folder='static', template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    return countries

@auth_blueprint.route('/check_username', methods=['POST'])
def check_username():
    username = request.form['username']
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT COUNT(*) AS count FROM users WHERE Username = %s', (username,))
    result = cursor.fetchone()
    cursor.close()
    if result['count'] > 0:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})

@auth_blueprint.route('/check_email', methods=['POST'])
def check_email():
    email = request.form['email']
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT COUNT(*) AS count FROM users WHERE email = %s', (email,))
    result = cursor.fetchone()
    cursor.close()
    if result['count'] > 0:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})
    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def save_user_data(data, profile_pic_filename=None):
    hashed_password = hash_password(data['password'])
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    profile_pic_path = f'uploads/{profile_pic_filename}' if profile_pic_filename else None
    
    cursor.execute('''
        INSERT INTO users (username, email, password, first_name, last_name, phone_number, birthdate, Address, nationality, profile_pic_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (data['username'], data['email'], hashed_password, data['FirstName'], data['LastName'], data['PhoneNumber'], data['BirthDate'], data['Address'], data['country'], profile_pic_path))
    
    current_app.mysql.connection.commit()

@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    countries = get_countries()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        first_name = form.FirstName.data
        last_name = form.LastName.data
        phone_number = form.PhoneNumber.data
        birthdate = form.BirthDate.data
        country = form.country.data
        address = form.Address.data
        terms = form.terms.data

        if user_exists(email):
            flash("User with the same email already exists", 'danger')
            return redirect(url_for('auth_blueprint.signup'))

        if username_exists(username):
            flash("Username is already taken", 'danger')
            return redirect(url_for('auth_blueprint.signup'))

        profile_pic_filename = None
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic.filename != '':
                if allowed_file(profile_pic.filename):
                    filename = secure_filename(profile_pic.filename)
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    profile_pic_path = os.path.join(upload_folder, filename)
                    profile_pic.save(profile_pic_path)
                    profile_pic_filename = filename
                else:
                    flash('Invalid file type! Please upload only JPG, PNG, or JPEG.', 'danger')
                    return redirect(request.url)
        
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'FirstName': first_name,
            'LastName': last_name,
            'PhoneNumber': phone_number,
            'BirthDate': birthdate,
            'country': country,
            'Address': address,
            'terms': terms,
            'profile_pic_path': f'uploads/{profile_pic_filename}' if profile_pic_filename else None
        }

        try:
            save_user_data(user_data, profile_pic_filename)
            flash('You have successfully registered!', 'success')
            return redirect(url_for('auth_blueprint.signin'))
        except Exception as e:
            print(f"Error saving user data: {e}")  # Debug: Print error if saving fails
            flash('An error occurred while registering. Please try again.', 'danger')
            return redirect(url_for('auth_blueprint.signup'))
    else:
        print(form.errors)  # Debug: Print form errors if validation fails

    return render_template('signup.html', form=form, countries=countries)

def user_exists(email):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    account = cursor.fetchone()
    return bool(account)

def username_exists(username):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    account = cursor.fetchone()
    return bool(account)


@auth_blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()  
    return redirect(url_for('auth_blueprint.signin'))

@auth_blueprint.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            if account['isBanned']:
                flash('Your account is banned. Please contact support.', 'signin_error')
            elif bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
                session['id'] = account['id']
                session['first_name'] = account['first_name']
                session['last_name'] = account['last_name']
                session['email'] = account['email']
                session['phone_number'] = account['phone_number']
                session['username'] = account['username']
                session['birthdate'] = account['birthdate'].strftime('%Y-%m-%d') if account['birthdate'] else None
                session['Address'] = account['Address']
                session['nationality'] = account['nationality']
                session['profile_pic_path'] = account['profile_pic_path']
                session['isAdmin'] = account['isAdmin']
                cursor.close()
                return redirect(url_for('home_blueprint.home'))

        cursor.close()
        flash('Invalid email or password!', 'signin_error')

    return render_template('signin.html', form=form)

@auth_blueprint.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    form = RecoverPasswordForm()
    
    if form.validate_on_submit():
        last_code_time = session.get('last_code_time')
        if last_code_time and time.time() - last_code_time < 30:
            flash('Please wait 30 seconds before requesting a new code.', 'error')
            return redirect(url_for('auth_blueprint.recover_password'))
        
        email = form.email.data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user:
            verification_code = ''.join(random.choices(string.digits, k=6))
            session['verification_code'] = verification_code
            session['email'] = email
            session['last_code_time'] = time.time()
            
            msg = Message('Password Recovery', sender='linkme.pfa@gmail.com', recipients=[email])
            msg.body = f'Your verification code is {verification_code}. This is a message from LinkMe team.'
            mail.send(msg)
            
            flash('Verification code sent to your email.', 'success')
            return redirect(url_for('auth_blueprint.verify_code'))
        else:
            flash('Email does not exist.', 'error')
    
    return render_template('recoverAccount.html', form=form)

@auth_blueprint.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    form = VerifyCodeForm()
    
    if form.validate_on_submit():
        code = form.code.data
        
        if code == session.get('verification_code'):
            session.pop('verification_code', None)  # Clear verification code from session
            return redirect(url_for('auth_blueprint.new_password'))
        else:
            flash('Invalid verification code.', 'error')
            return redirect(url_for('auth_blueprint.verify_code'))
    
    return render_template('verifyCode.html', form=form)

@auth_blueprint.route('/new_password', methods=['GET', 'POST'])
def new_password():
    form = NewPasswordForm()
    
    if form.validate_on_submit():
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth_blueprint.new_password'))
        
        email = session.get('email')
        hashed_password = hash_password(password)  # Hash the new password
        
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE users SET password = %s WHERE email = %s', (hashed_password, email))
        mysql.connection.commit()
        cursor.close()
        
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth_blueprint.signin'))
    
    return render_template('newPassword.html', form=form)
