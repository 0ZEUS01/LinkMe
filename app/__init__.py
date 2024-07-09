from flask import Flask
from flask_mysqldb import MySQL
from flask_mail import Mail

mysql = MySQL()
mail = Mail()

def create_app():
    app = Flask(__name__, static_url_path='/static')

    from app.blueprints.auth.auth import auth_blueprint
    from app.blueprints.profile.profile import profile_blueprint
    from app.blueprints.job.job import job_blueprint
    from app.blueprints.home.home import home_blueprint
    from app.blueprints.admin.admin import admin_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(profile_blueprint, url_prefix='/profile')
    app.register_blueprint(job_blueprint)
    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint)
    
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'LinkMe' 
    app.config['UPLOAD_FOLDER'] = 'C:/Users/Yahya/Desktop/LinkMe/app/blueprints/profile/static/uploads'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'linkme.pfa@gmail.com'
    app.config['MAIL_PASSWORD'] = 'xnlu tiba ewyn dgzc'#'WeAreLinkMeTeam'  
    app.config['MAIL_DEFAULT_SENDER'] = ('LinkMe Team', 'linkme.pfa@gmail.com')

    mail.init_app(app)
    
    mysql.init_app(app)
    app.mysql = mysql

    return app
