from flask import Blueprint, render_template, redirect, url_for, request, session, current_app, flash, jsonify
from werkzeug.utils import secure_filename
import os
import MySQLdb.cursors

profile_blueprint = Blueprint('profile_blueprint', __name__, static_folder='static', template_folder='templates')


def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    return countries

@profile_blueprint.route('/profile', methods=['GET'])
def profile():
    if 'email' in session and 'username' in session:
        email = session['email']
        username = session['username']
        countries = get_countries()
        
        cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            if user_data['profile_pic_path']:
                user_data['profile_pic_path'] = user_data['profile_pic_path'].replace(
                    'C:\\Users\\Yahya\\Desktop\\LinkMe\\app\\static\\', '')
            return render_template('profile.html', email=email, username=username, user=user_data, countries=countries)
        else:
            flash('User data not found!', 'danger')
            return redirect(url_for('auth_blueprint.signin'))
    else:
        return redirect(url_for('auth_blueprint.signin'))
