from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    """
    Paramètres de création de l'application flask, import des routes et enregistrement des blueprints
    """
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = "mariadb+mariadbconnector://qamu:qamu@127.0.0.1/sae302"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'b8c44d9164252085c7ed0c852f632cf82a5aa8c8e785b12f6e47c80822b8c225'
    app.config.from_object('config.Config')
    db.init_app(app)
    
    from app.routes import auth_bp, user_bp, serveurs_bp, journaux_bp
    
    app.register_blueprint(auth_bp, url_prefix="")
    app.register_blueprint(user_bp, url_prefix="")
    app.register_blueprint(serveurs_bp, url_prefix="")
    app.register_blueprint(journaux_bp, url_prefix="")

    with app.app_context():
        db.create_all()   
    return app