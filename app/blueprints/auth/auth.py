import os
import bcrypt
from flask import Flask, render_template, redirect, url_for, flash, session, current_app
from flask import Blueprint
from .forms import SignupForm, SigninForm
from werkzeug.utils import secure_filename
import MySQLdb.cursors

auth_blueprint = Blueprint('auth_blueprint', __name__, static_folder='static', template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    return countries

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
@auth_blueprint.route('/', methods=['GET', 'POST'])
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
        if form.picture.data:
            picture = form.picture.data
            if picture and allowed_file(picture.filename):
                profile_pic_filename = secure_filename(picture.filename)
                picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], profile_pic_filename))
            else:
                flash("Invalid file type for profile picture. Allowed types are JPG and PNG.", 'danger')
                return redirect(url_for('auth_blueprint.signup'))

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
    session.pop('email', None)
    session.pop('username', None)
    session.pop('id',None)
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

        if account and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
            session['email'] = email
            session['username'] = account['username']
            session['id'] = account['id']
            cursor.close()
            return redirect(url_for('profile_blueprint.profile'))
        
        cursor.close()
        flash('Invalid email or password!', 'danger')

    return render_template('signin.html', form=form)
