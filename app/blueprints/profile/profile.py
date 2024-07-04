from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from werkzeug.utils import secure_filename
import os
import MySQLdb.cursors

profile_blueprint = Blueprint('profile_blueprint', __name__, static_folder='static', template_folder='templates')

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    cursor.close()
    return countries

@profile_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'id' in session and 'email' in session and 'username' in session:
        email = session['email']
        username = session['username']
        id = session['id']
        countries = get_countries()

        cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            username = request.form['organization']
            email = request.form['email']
            phone_number = request.form['phoneNumber']
            country_id = request.form['country']
            address = request.form['address']

            # Update user data in the database
            cursor.execute('UPDATE users SET first_name=%s, last_name=%s, username=%s, email=%s, phone_number=%s, nationality=%s, address=%s WHERE id=%s',
                            (first_name, last_name, username, email, phone_number, country_id, address, id))
            current_app.mysql.connection.commit()
            flash('Profile updated successfully!', 'success')

            # Redirect to the profile page again to reflect changes
            return redirect(url_for('profile_blueprint.profile'))

        # Fetch user data to display in the profile form
        cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data:
            if user_data['profile_pic_path']:
                user_data['profile_pic_path'] = user_data['profile_pic_path'].replace(
                    'C:\\Users\\Yahya\\Desktop\\LinkMe\\app\\static\\', '')
            return render_template('profile.html', id=id, email=email, username=username, user=user_data, countries=countries)
        else:
            flash('User data not found!', 'danger')
            return redirect(url_for('auth_blueprint.signin'))
    else:
        return redirect(url_for('auth_blueprint.signin'))
