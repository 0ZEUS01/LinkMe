from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from werkzeug.utils import secure_filename
import os
import bcrypt
import MySQLdb.cursors

profile_blueprint = Blueprint('profile_blueprint', __name__, static_folder='static', template_folder='templates')

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    cursor.close()
    return countries

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

@profile_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'id' in session and 'email' in session and 'username' in session:
        email = session['email']
        username = session['username']
        id = session['id']
        countries = get_countries()

        cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST':
            print("Form submitted")
            print("Form data:", request.form)

            old_password = request.form.get('OldPassword')
            new_password = request.form.get('NewPassword')
            confirm_new_password = request.form.get('ConfirmNewPassword')

            if old_password or new_password or confirm_new_password:
                # Check if new password and confirm new password match
                if new_password != confirm_new_password:
                    flash('New passwords do not match!', 'danger')
                    return redirect(url_for('profile_blueprint.profile'))

                # Fetch the current password from the database
                cursor.execute('SELECT password FROM users WHERE id = %s', (id,))
                user = cursor.fetchone()

                # Verify the old password
                if not check_password(user['password'], old_password):
                    flash('Old password is incorrect!', 'danger')
                    return redirect(url_for('profile_blueprint.profile'))

                # Hash the new password
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                # Update the password in the database
                cursor.execute('UPDATE users SET password=%s WHERE id=%s', (hashed_password, id))
                current_app.mysql.connection.commit()
                flash('Password updated successfully!', 'success')

            else:
                print("Updating profile details")
                first_name = request.form.get('firstName')
                last_name = request.form.get('lastName')
                organization = request.form.get('organization')
                email = request.form.get('email')
                phone_number = request.form.get('phoneNumber')
                country_id = request.form.get('country')
                address = request.form.get('address')

                print("Profile details:", first_name, last_name, organization, email, phone_number, country_id, address)

                # Update user data in the database
                cursor.execute('UPDATE users SET first_name=%s, last_name=%s, username=%s, email=%s, phone_number=%s, nationality=%s, address=%s WHERE id=%s',
                                (first_name, last_name, organization, email, phone_number, country_id, address, id))
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
