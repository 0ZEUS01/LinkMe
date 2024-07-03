import os
from flask import Blueprint, render_template, redirect, url_for, request, session, current_app, flash
from .forms import SignupForm, SigninForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors

auth_blueprint = Blueprint('auth_blueprint', __name__, static_folder='static', template_folder='templates')

UPLOAD_FOLDER = 'C:\\Users\\Yahya\\Desktop\\LinkMe\\app\\static\\users_pfp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_data(data, profile_pic_filename=None):
    cursor = current_app.mysql.connection.cursor()
    if profile_pic_filename:
        profile_pic_path = os.path.join(UPLOAD_FOLDER, profile_pic_filename)
    else:
        profile_pic_path = None
    
    cursor.execute('''
        INSERT INTO users (username, email, password, first_name, last_name, phone_number, birthdate, Address, nationality, profile_pic_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (data['username'], data['email'], data['password'], data['FirstName'], data['LastName'], data['PhoneNumber'], data['BirthDate'], data['Address'], data['country'], profile_pic_path))
    
    current_app.mysql.connection.commit()

def user_exists(email):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    account = cursor.fetchone()
    if account:
        return True
    return False

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    return countries


def valid_user(email, password):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    account = cursor.fetchone()
    if account:
        # Check if the hashed password matches the provided password
        if check_password_hash(account['password'], password):
            return True
    return False

def get_name_from_email(email):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT username FROM users WHERE email = %s', (email,))
    account = cursor.fetchone()
    if account:
        return account['username']
    return ''

@auth_blueprint.route('/logout', methods=['GET'])
def logout():
    session.pop('email')
    session.pop('username')
    return redirect('/signin')

@auth_blueprint.route('/', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    countries = get_countries()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data, method='scrypt')
        first_name = form.FirstName.data
        last_name = form.LastName.data
        phone_number = form.PhoneNumber.data
        birthdate = form.BirthDate.data
        country = form.country.data
        address = form.Address.data
        terms = form.terms.data

        if user_exists(email):
            flash("User with same email already exists", 'danger')
            return redirect(url_for('auth_blueprint.signup'))

        profile_pic_filename = None
        if form.picture.data:
            picture = form.picture.data
            if picture and allowed_file(picture.filename):
                profile_pic_filename = secure_filename(picture.filename)
                picture.save(os.path.join(UPLOAD_FOLDER, profile_pic_filename))
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
            'terms': terms
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



@auth_blueprint.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if valid_user(email, password):  # Assuming valid_user checks credentials
            session['email'] = email
            session['username'] = get_name_from_email(email)
            
            # Check if the user has at least one skill entry
            cursor = current_app.mysql.connection.cursor()
            cursor.execute('''
                SELECT COUNT(*) AS count_skills
                FROM user_skills
                WHERE email = %s
            ''', (email,))
            count_skills = cursor.fetchone()[0]  # Access the count directly
            
            if count_skills > 0:
                # User has at least one skill, redirect to view profile
                return redirect(url_for('profile_blueprint.view_profile'))
            else:
                # User has not entered any skills, redirect to edit profile
                return redirect(url_for('profile_blueprint.edit_profile'))
            
        flash('Invalid email or password!', 'danger')
    
    return render_template('signin.html', form=form)
