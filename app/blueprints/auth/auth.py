from flask import Flask, render_template, redirect, url_for, flash, session,current_app
from flask import Blueprint
from .forms import SignupForm, SigninForm
import MySQLdb.cursors

auth_blueprint = Blueprint('auth_blueprint', __name__, static_folder='static', template_folder='templates')

def save_user_data(data):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (data['username'], data['email'], data['password']))
    current_app.mysql.connection.commit()

def user_exists(email):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    account = cursor.fetchone()
    if account:
        return True
    return False

def valid_user(email, password):
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
    account = cursor.fetchone()
    if account:
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
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if user_exists(email):
            return "User with same email already exists"
        user_data = {'username': username, 'email': email, 'password': password}
        save_user_data(user_data)
        return redirect(url_for('auth_blueprint.signin'))
    return render_template('signup.html', form=form)

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
            
        return 'Invalid email or password!'
    
    return render_template('signin.html', form=form)