
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import os
import bcrypt
import MySQLdb.cursors

profile_blueprint = Blueprint('profile_blueprint', __name__, static_folder='static', template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Update UPLOAD_FOLDER to the desired path
UPLOAD_FOLDER = 'C:/Users/Yahya/Desktop/LinkMe/app/blueprints/profile/static/uploads'
profile_blueprint.config = {'UPLOAD_FOLDER': UPLOAD_FOLDER}

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    cursor.close()
    return countries

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_user_data(data, profile_pic_filename=None):
    hashed_password = hash_password(data['password'])
    cursor = current_app.mysql.connection.cursor()

    if profile_pic_filename:
        profile_pic_path = f'uploads/{profile_pic_filename}'
    else:
        # Keep the existing profile picture path if no new picture is uploaded
        profile_pic_path = data['profile_pic_path']

    try:
        cursor.execute('''
            UPDATE users 
            SET first_name=%s, last_name=%s, username=%s, email=%s, phone_number=%s, nationality=%s, address=%s, profile_pic_path=%s
            WHERE id=%s
        ''', (data['firstName'], data['lastName'], data['Username'], data['email'], data['phoneNumber'], data['country'], data['address'], profile_pic_path, data['id']))
        
        current_app.mysql.connection.commit()
    except Exception as e:
        current_app.logger.error(f"Error saving user data: {e}")
        raise
    finally:
        cursor.close()

@profile_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'id' in session and 'email' in session and 'username' in session:
        email = session['email']
        username = session['username']
        id = session['id']
        countries = get_countries()

        cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
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
                        profile_pic_path = profile_pic_path.replace('\\', '/')
                    else:
                        flash('Invalid file type! Please upload only JPG, PNG, or JPEG.', 'danger')
                        return redirect(request.url)
                else:
                    profile_pic_path = request.form.get('original_profile_pic')

                # Update profile picture path in user data
                user_data = {
                    'id': id,
                    'firstName': request.form.get('firstName'),
                    'lastName': request.form.get('lastName'),
                    'Username': request.form.get('Username'),
                    'email': request.form.get('email'),
                    'phoneNumber': request.form.get('phoneNumber'),
                    'country': request.form.get('country'),
                    'address': request.form.get('address'),
                    'password': '',  # Assuming password is not updated here
                    'profile_pic_path': filename if profile_pic.filename else request.form.get('original_profile_pic')
                }

                try:
                    save_user_data(user_data, filename if profile_pic.filename else None)
                    flash('Profile picture updated successfully!', 'success')
                except Exception as e:
                    flash('An error occurred while updating profile picture.', 'danger')
                    current_app.logger.error(f"Error updating profile picture: {e}")

                return redirect(url_for('.profile'))

            # Handle other form fields update here
            # This part should handle updating other profile information
            user_data = {
                'id': id,
                'firstName': request.form.get('firstName'),
                'lastName': request.form.get('lastName'),
                'Username': request.form.get('Username'),
                'email': request.form.get('email'),
                'phoneNumber': request.form.get('phoneNumber'),
                'country': request.form.get('country'),
                'address': request.form.get('address'),
                'password': '',  # Assuming password is not updated here
                'profile_pic_path': request.form.get('original_profile_pic')
            }

            try:
                save_user_data(user_data)
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                flash('An error occurred while updating profile.', 'danger')
                current_app.logger.error(f"Error updating profile: {e}")

            return redirect(url_for('.profile'))  # Redirect to profile page after updating

        cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            if user_data['profile_pic_path']:
                user_data['profile_pic_path'] = user_data['profile_pic_path'].replace('profile/static/', '')
            return render_template('profile.html', id=id, email=email, username=username, user=user_data, countries=countries)
        else:
            flash('User data not found!', 'danger')
            return redirect(url_for('auth_blueprint.signin'))
    else:
        return redirect(url_for('auth_blueprint.signin'))
