from flask import Blueprint, current_app, render_template, session
from MySQLdb.cursors import DictCursor

home_blueprint = Blueprint('home_blueprint', __name__, template_folder='templates', static_folder='static')

def get_user_details(user_id):
    cursor = current_app.mysql.connection.cursor(DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return user

def is_admin(user_id):
    user = get_user_details(user_id)
    print(f"User details: {user}")  # Debug print
    if user and user['isAdmin'] == 1:
        return True
    return False


@home_blueprint.route('/home', methods=['GET'])
def home():
    if 'id' in session:
        user_id = session.get('id')
        print(f"User ID from session: {user_id}")  # Debug print
        isAdmin = is_admin(user_id)
        print(f"isAdmin: {isAdmin}")  # Debug print
        return render_template('home.html', isAdmin=isAdmin)
    else:
        return render_template('guest_home.html')  # Render guest_home if not logged in


@home_blueprint.route('/', methods=['GET'])
def guest_home():
    return render_template('guest_home.html')
