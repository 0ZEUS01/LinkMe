from flask import Blueprint, render_template

home_blueprint = Blueprint('home_blueprint', __name__, template_folder='templates', static_folder='static')

@home_blueprint.route('/home', methods=['GET'])
def home():
    return render_template('home.html')
