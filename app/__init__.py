from flask import Flask, jsonify
from flask_migrate import Migrate
from .config import Config
from .db import db
from .auth import auth_bp
from .routes import routes_bp


migrate = Migrate()


def create_app(config_cls = Config) -> Flask:

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_cls)

    app.config['SECRET_KEY'] = 'your secret key'

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    @app.cli.command('init-db')
    def init_db_command():
        from .models import Player

        with app.app_context():
            if not Player.query.get(1):
                admin = Player('admin', 'admin@gmail.com', '123')
                db.session.add(admin)
                db.session.commit()
    
    @app.errorhandler(400)
    def bad_request(error: Exception):
        return jsonify({
            "error": repr(error),
            "message": 'Bad request 400 :('
        }), 400
    

    @app.errorhandler(401)
    def unauthorized(error: Exception):
        return jsonify({
            "error": repr(error),
            "message": 'Unauthorized 401 :('
        }), 401
    

    @app.errorhandler(404)
    def not_found(error: Exception):
        return jsonify({
            "error": repr(error),
            "message": 'Not found 404 :('
        }), 404
    

    @app.errorhandler(500)
    def internal_server_error(error: Exception):
        return jsonify({
            "error": repr(error),
            "message": 'Internal server error 500 :('
        }), 500
    

    @app.errorhandler(503)
    def service_unavailable(error: Exception):
        return jsonify({
            "error": repr(error),
            "message": 'Service unavailable 503 :('
        }), 503

    
    return app
