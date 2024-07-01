from flask import Blueprint, render_template, redirect, url_for, request, session, current_app, flash, jsonify
from werkzeug.utils import secure_filename
import os
import MySQLdb.cursors

profile_blueprint = Blueprint('profile_blueprint', __name__, static_folder='static', template_folder='templates')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_blueprint.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'email' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    if request.method == 'POST':
        email = session['email']
        experiences = request.form.getlist('experience_title')  # List of experience titles
        descriptions = request.form.getlist('experience_description')  # List of experience descriptions
        start_dates = request.form.getlist('experience_start_date')  # List of experience start dates
        end_dates = request.form.getlist('experience_end_date')  # List of experience end dates
        skills = request.form['skills'].split(',')  # List of skills
        profile_pic = None

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                profile_pic_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(profile_pic_path)
                profile_pic = f'static/uploads/{filename}'

        cursor = current_app.mysql.connection.cursor()

        # Insert or update profile picture
        if profile_pic:
            cursor.execute('''
                INSERT INTO profile_pictures (email, profile_pic_path)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                profile_pic_path = VALUES(profile_pic_path)
            ''', (email, profile_pic))

        # Insert experiences
        cursor.execute('DELETE FROM experiences WHERE email = %s', (email,))
        for i in range(len(experiences)):
            cursor.execute('''
                INSERT INTO experiences (email, title, description, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s)
            ''', (email, experiences[i], descriptions[i], start_dates[i], end_dates[i]))

        # Insert user skills
        cursor.execute('DELETE FROM user_skills WHERE email = %s', (email,))
        # Update user skills
        for skill in skills:
            cursor.execute('''
                INSERT IGNORE INTO skills (skill_name)
                VALUES (%s)
            ''', (skill.strip(),))

            cursor.execute('''
                INSERT INTO user_skills (email, skill_id)
                SELECT %s, skill_id FROM skills WHERE skill_name = %s
            ''', (email, skill.strip()))

        current_app.mysql.connection.commit()

        flash('Profile updated successfully!')
        return redirect(url_for('profile_blueprint.view_profile'))

    return render_template('edit_profile.html')


@profile_blueprint.route('/view', methods=['GET'])
def view_profile():
    if 'email' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    email = session['email']
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch profile picture
    cursor.execute('SELECT profile_pic_path FROM profile_pictures WHERE email = %s', (email,))
    profile_pic = cursor.fetchone()

    # Fetch experiences
    cursor.execute('SELECT title, description, start_date, end_date FROM experiences WHERE email = %s', (email,))
    experiences = cursor.fetchall()

    # Fetch skills
    cursor.execute('''
        SELECT skill_name
        FROM user_skills
        JOIN skills ON user_skills.skill_id = skills.skill_id
        WHERE user_skills.email = %s
    ''', (email,))
    skills = [row['skill_name'] for row in cursor.fetchall()]

    # Fetch username
    cursor.execute('SELECT username FROM users WHERE email = %s', (email,))
    username = cursor.fetchone()

    user_details = {
        'profile_pic': profile_pic['profile_pic_path'] if profile_pic else None,
        'experiences': experiences,
        'skills': skills,
        'username': username['username'] if username else 'No username available'
    }

    return render_template('view_profile.html', user_details=user_details)


@profile_blueprint.route('/update', methods=['GET', 'POST'])
def update_profile():
    if 'email' not in session:
        return redirect(url_for('auth_blueprint.signin'))

    if request.method == 'POST':
        email = session['email']
        experiences = request.form.getlist('experience_title')  # List of experience titles
        descriptions = request.form.getlist('experience_description')  # List of experience descriptions
        start_dates = request.form.getlist('experience_start_date')  # List of experience start dates
        end_dates = request.form.getlist('experience_end_date')  # List of experience end dates
        skills = request.form['skills'].split(',')  # List of skills
        profile_pic = None

        cursor = current_app.mysql.connection.cursor()

        # Update profile picture
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                profile_pic_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(profile_pic_path)
                profile_pic = f'static/uploads/{filename}'
                cursor.execute('''
                    UPDATE profile_pictures
                    SET profile_pic_path = %s
                    WHERE email = %s
                ''', (profile_pic, email))

        # Update experiences
        cursor.execute('DELETE FROM experiences WHERE email = %s', (email,))
        for title, description, start_date, end_date in zip(experiences, descriptions, start_dates, end_dates):
            cursor.execute('''
                INSERT INTO experiences (email, title, description, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                description = VALUES(description),
                start_date = VALUES(start_date),
                end_date = VALUES(end_date)
            ''', (email, title, description, start_date, end_date))
        cursor.execute('DELETE FROM user_skills WHERE email = %s', (email,))
        # Update user skills
        for skill in skills:
            cursor.execute('''
                INSERT IGNORE INTO skills (skill_name)
                VALUES (%s)
            ''', (skill.strip(),))

            cursor.execute('''
                INSERT INTO user_skills (email, skill_id)
                SELECT %s, skill_id FROM skills WHERE skill_name = %s
            ''', (email, skill.strip()))

        current_app.mysql.connection.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile_blueprint.view_profile'))

    # If GET request, render the profile update form
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    email = session['email']
    cursor.execute('SELECT profile_pic_path FROM profile_pictures WHERE email = %s', (email,))
    profile_pic = cursor.fetchone()
    cursor.execute('SELECT title, description, start_date, end_date FROM experiences WHERE email = %s', (email,))
    experiences = cursor.fetchall()
    cursor.execute('''
        SELECT skill_name
        FROM user_skills
        JOIN skills ON user_skills.skill_id = skills.skill_id
        WHERE user_skills.email = %s
    ''', (email,))
    skills = [row['skill_name'] for row in cursor.fetchall()]

    user_details = {
        'profile_pic': profile_pic['profile_pic_path'] if profile_pic else None,
        'experiences': experiences,
        'skills': skills
    }
    return render_template('update.html', user_details=user_details)


@profile_blueprint.route('/skills', methods=['GET'])
def get_skills():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT skill_name FROM skills')
    skills = [row['skill_name'] for row in cursor.fetchall()]
    return jsonify(skills)

