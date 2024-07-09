import MySQLdb
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from MySQLdb.cursors import DictCursor

admin_blueprint = Blueprint('admin_blueprint', __name__, template_folder='templates', static_folder='static')

def get_user_details(user_id):
    cursor = current_app.mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

def is_admin(user_id):
    user = get_user_details(user_id)
    if user and user['isAdmin'] == 1:
        return True
    return False

def get_all_users():
    cursor = current_app.mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    return users

def get_countries():
    cursor = current_app.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT country_id, country_name FROM country')
    countries = cursor.fetchall()
    cursor.close()
    return countries

@admin_blueprint.route('/admin', methods=['GET'])
def admin():
    if 'id' in session:
        user_id = session.get('id')
        isAdmin = is_admin(user_id)
        if isAdmin:
            return render_template('admin.html', isAdmin=isAdmin, countries=get_countries(), user=get_all_users())
        else:
            flash('Access denied: This route is only for website admins.', 'error')
            return redirect(url_for('home.html'))  

    flash('You need to log in to access this page.', 'error')
    return redirect(url_for('signin.html'))

def search_users(query):
    cursor = current_app.mysql.connection.cursor(DictCursor)
    search_query = f"%{query}%"
    cursor.execute('SELECT * FROM users WHERE first_name LIKE %s OR last_name LIKE %s', (search_query, search_query))
    users = cursor.fetchall()
    cursor.close()
    return users


@admin_blueprint.route('/search_users', methods=['GET'])
def search_users_route():
    query = request.args.get('query', '')
    users = search_users(query)
    return jsonify(users)

@admin_blueprint.route('/toggle_ban_user', methods=['POST'])
def toggle_ban_user():
    if 'id' not in session or not is_admin(session['id']):
        flash('Access denied: This action is only for website admins.', 'error')
        return redirect(url_for('admin_blueprint.admin'))

    user_id_to_toggle = request.form.get('user_id')
    if not user_id_to_toggle:
        flash('No user specified.', 'error')
        return redirect(url_for('admin_blueprint.admin'))

    cursor = current_app.mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT isBanned FROM users WHERE id = %s', (user_id_to_toggle,))
    user = cursor.fetchone()

    if user:
        new_ban_status = not user['isBanned']
        cursor.execute('UPDATE users SET isBanned = %s WHERE id = %s', (new_ban_status, user_id_to_toggle))
        current_app.mysql.connection.commit()
        cursor.close()

        if new_ban_status:
            flash('User has been banned successfully.', 'success')
        else:
            flash('User has been unbanned successfully.', 'success')
    else:
        flash('User not found.', 'error')
        cursor.close()

    return redirect(url_for('admin_blueprint.admin'))

