from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()
def create_app():
    app = Flask(__name__)

    from app.blueprints.auth.auth import auth_blueprint
    from app.blueprints.profile.profile import profile_blueprint
    from app.blueprints.job.job import job_blueprint
    app.register_blueprint(job_blueprint)
    app.register_blueprint(profile_blueprint, url_prefix='/profile')
    app.register_blueprint(auth_blueprint)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'LinkMe' 
    app.config['UPLOAD_FOLDER'] = 'C:/Users/Yahya/Desktop/LinkMe/app/blueprints/profile/static/uploads'
    mysql.init_app(app)
    app.mysql = mysql
    return app