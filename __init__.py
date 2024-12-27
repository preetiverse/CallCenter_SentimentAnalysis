from flask import Flask

def create_app():
    app = Flask(__name__)
    # Load configuration from config.py
    app.config.from_pyfile('config.py')

    # Import and register the routes Blueprint
    from app.routes import routes
    app.register_blueprint(routes)

    return app
