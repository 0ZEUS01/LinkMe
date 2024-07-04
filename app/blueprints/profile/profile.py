from flask import Blueprint, render_template, redirect, url_for, request, session, current_app, flash, jsonify
from werkzeug.utils import secure_filename
import os
import MySQLdb.cursors

profile_blueprint = Blueprint('profile_blueprint', __name__, static_folder='static', template_folder='templates')

@profile_blueprint.route('/profile', methods=['GET'])
def profile():
    if 'email' in session and 'username' in session:
        email = session['email']
        username = session['username']
        return render_template('profile.html', email=email, username=username)
    else:
        return redirect(url_for('auth_blueprint.signin'))