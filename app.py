import os
from flask import Flask, redirect, url_for
from models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    db.init_app(app)
    
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.chantiers import chantiers_bp
    from routes.saisies import saisies_bp
    from routes.validation import validation_bp
    from routes.users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chantiers_bp)
    app.register_blueprint(saisies_bp)
    app.register_blueprint(validation_bp)
    app.register_blueprint(users_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    @app.context_processor
    def utility_processor():
        from utils import format_currency, format_percentage
        return dict(
            format_currency=format_currency,
            format_percentage=format_percentage
        )
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
