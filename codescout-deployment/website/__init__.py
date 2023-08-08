from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import json
from pathlib import Path
import logging as lg
from os import environ
from pathlib import Path

# Initialize SQLAlchemy
db = SQLAlchemy()

# Create a login manager, redirects to login page if you click on login only 
# content while not logged in.
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Setup logging to go to CODE_SCOUT_HOME/logs/flask.app.log file.
lg.basicConfig(
    filename=str(Path(environ.get("CODE_SCOUT_HOME")) / Path('logs/flask.app.log')), 
    level=lg.DEBUG, format='[%(asctime)s] %(levelname)s --> %(module)s - %(message)s'
)

def create_app():
    # Initialize the Flask instance.
    app = Flask(__name__)

    # Set the project root.
    app.config['PROJECT_ROOT'] = Path(__file__).parent

    # Open the app config JSON file and import the necessary information into 
    # the app configuration.
    with open(str(app.config['PROJECT_ROOT'] / Path('app_config.json'))) as conf:
        config = json.load(conf)

        # The webserver secret key.
        app.config['SECRET_KEY'] = config['SECRET_KEY']

        # SQLAlchemy URI defines how to connect to Postgres.
        app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']

        # Page lengths for how many elements to display on paginations.
        app.config['SEARCH_PAGE_LEN'] = config["SEARCH_PAGE_LEN"]
        app.config['USER_PAGE_LEN'] = config["USER_PAGE_LEN"]

        # Key used to encrypt user ElasticSearch login info.
        app.config['ENCRYPTION_KEY'] = config["ENCRYPTION_KEY"]

    # Initialize SQLAlchemy and Login Manager instance with app.
    db.init_app(app=app)
    login_manager.init_app(app=app)

    # Create a blueprint which handles user auth.
    from website.auth.routes import auth
    app.register_blueprint(auth)

    # Create a blueprint which handles normal functions.
    from website.main.routes import main
    app.register_blueprint(main)

    app.logger.info('Flask App Configured.')

    return app
