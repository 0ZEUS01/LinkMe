
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
                    'password': '', 
                    'profile_pic_path': filename if profile_pic.filename else request.form.get('original_profile_pic')
                }

                try:
                    save_user_data(user_data, filename if profile_pic.filename else None)
                    flash('Profile picture updated successfully!', 'success')
                except Exception as e:
                    flash('An error occurred while updating profile picture.', 'danger')
                    current_app.logger.error(f"Error updating profile picture: {e}")

                return redirect(url_for('.profile'))

            user_data = {
                'id': id,
                'firstName': request.form.get('firstName'),
                'lastName': request.form.get('lastName'),
                'Username': request.form.get('Username'),
                'email': request.form.get('email'),
                'phoneNumber': request.form.get('phoneNumber'),
                'country': request.form.get('country'),
                'address': request.form.get('address'),
                'password': '',  
                'profile_pic_path': request.form.get('original_profile_pic')
            }

            try:
                save_user_data(user_data)
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                flash('An error occurred while updating profile.', 'danger')
                current_app.logger.error(f"Error updating profile: {e}")

            return redirect(url_for('.profile')) 

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

@profile_blueprint.route('/profile/changePassword', methods=['POST'])
def change_password():
    if 'id' in session:
        user_id = session['id']
        old_password = request.form.get('OldPassword')
        new_password = request.form.get('NewPassword')
        confirm_new_password = request.form.get('ConfirmNewPassword')

        if new_password != confirm_new_password:
            flash('New password and confirmation do not match!', 'danger')
            return redirect(url_for('.profile'))

        cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT password FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()

        if user and check_password(user['password'], old_password):
            hashed_new_password = hash_password(new_password)
            try:
                cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_new_password, user_id))
                current_app.mysql.connection.commit()
                flash('Password updated successfully!', 'success')
            except Exception as e:
                current_app.logger.error(f"Error updating password: {e}")
                flash('An error occurred while updating the password.', 'danger')
            finally:
                cursor.close()
        else:
            flash('Old password is incorrect!', 'danger')

        return redirect(url_for('.profile'))
    else:
        return redirect(url_for('auth_blueprint.signin'))

@profile_blueprint.route('/experiences', methods=['GET'])
def experiences():
    if 'id' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    user_id = session['id']
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM experiences WHERE id = %s', (user_id,))
    experiences = cursor.fetchall()
    cursor.close()

    return render_template('experience.html', experiences=experiences)


@profile_blueprint.route('/add_experience', methods=['POST'])
def add_experience():
    if 'id' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    user_id = session['id']
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    experience_title = request.form.get('ExperienceTitle')
    description = request.form.get('Description')
    start_date = request.form.get('startDate')
    end_date = request.form.get('endDate')

    cursor.execute('''
        INSERT INTO experiences (id, title, description, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
    ''', (user_id, experience_title, description, start_date, end_date))
    current_app.mysql.connection.commit()
    cursor.close()
    flash('Experience added successfully!', 'success')

    return redirect(url_for('profile_blueprint.experiences'))

@profile_blueprint.route('/edit_delete_experience', methods=['POST'])
def edit_delete_experience():
    if 'id' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    user_id = session['id']
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    experience_id = request.form.get('experience_id')
    experience_title_show = request.form.get('ExperienceTitleShow')
    description_show = request.form.get('DescriptionShow')
    start_date_show = request.form.get('startDateShow')
    end_date_show = request.form.get('endDateShow')

    if 'edit_experience' in request.form:
        cursor.execute('''
            UPDATE experiences 
            SET title=%s, description=%s, start_date=%s, end_date=%s
            WHERE experience_id=%s AND id=%s
        ''', (experience_title_show, description_show, start_date_show, end_date_show, experience_id, user_id))
        current_app.mysql.connection.commit()
        flash('Experience updated successfully!', 'success')

    elif 'delete_experience' in request.form:
        cursor.execute('DELETE FROM experiences WHERE experience_id=%s AND id=%s', (experience_id, user_id))
        current_app.mysql.connection.commit()
        flash('Experience deleted successfully!', 'success')

    cursor.close()
    return redirect(url_for('profile_blueprint.experiences'))

@profile_blueprint.route('/skills', methods=['GET'])
def skills():
    if 'id' not in session:
        return redirect(url_for('auth_blueprint.signin'))
    
    user_id = session['id']
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('''
        SELECT us.skill_id, s.skill_name
        FROM user_skills us
        JOIN skills s ON us.skill_id = s.skill_id
        WHERE us.id = %s
    ''', (user_id,))
    user_skills = cursor.fetchall()
    cursor.close()

    return render_template('skill.html', skills=user_skills)

@profile_blueprint.route('/add_skill', methods=['POST'])
def add_skill():
    if 'id' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    user_id = session['id']
    new_skill_name = request.form.get('newSkill')
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute('SELECT skill_id FROM skills WHERE skill_name = %s', (new_skill_name,))
    skill = cursor.fetchone()
    
    if skill:
        skill_id = skill['skill_id']
    else:
        cursor.execute('INSERT INTO skills (skill_name) VALUES (%s)', (new_skill_name,))
        current_app.mysql.connection.commit()
        skill_id = cursor.lastrowid
    
    cursor.execute('INSERT INTO user_skills (id, skill_id) VALUES (%s, %s)', (user_id, skill_id))
    current_app.mysql.connection.commit()
    cursor.close()
    flash('Skill added successfully!', 'success')
    
    return redirect(url_for('profile_blueprint.skills'))

@profile_blueprint.route('/suggest_skills', methods=['GET'])
def suggest_skills():
    query = request.args.get('query', '')
    if query:
        cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT skill_name FROM skills WHERE skill_name LIKE %s', ('%' + query + '%',))
        skills = cursor.fetchall()
        cursor.close()

        suggestions = ''.join([f"<div class='suggestion'>{skill['skill_name']}</div>" for skill in skills])
        return suggestions
    return ''


@profile_blueprint.route('/delete_skill', methods=['POST'])
def delete_skill():
    if 'id' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    user_id = session['id']
    skill_id = request.form.get('skill_id')

    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM user_skills WHERE id = %s AND skill_id = %s', (user_id, skill_id))
    current_app.mysql.connection.commit()
    cursor.close()
    
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('profile_blueprint.skills'))
