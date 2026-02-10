import os
from flask import Flask, redirect, url_for, session, request, g
from models import db
from config import Config
from lang import get_text

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
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
    from routes.finance import finance_bp
    from routes.superadmin import superadmin_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chantiers_bp)
    app.register_blueprint(saisies_bp)
    app.register_blueprint(validation_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(superadmin_bp)
    app.register_blueprint(admin_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.route('/set_language/<lang_code>')
    def set_language(lang_code):
        if lang_code in ['fr', 'en']:
            session['lang'] = lang_code

        referrer = request.referrer
        # Basic open redirect protection: ensure referrer is from same domain
        if referrer and request.host in referrer:
             return redirect(referrer)
        return redirect(url_for('index'))

    @app.before_request
    def load_user_language():
        lang = session.get('lang')
        if not lang:
            lang = request.accept_languages.best_match(['fr', 'en'])
        if not lang:
            lang = 'fr'
        g.lang = lang
    
    @app.context_processor
    def utility_processor():
        from utils import format_currency, format_percentage
        from datetime import datetime

        def t(key):
            return get_text(key, getattr(g, 'lang', 'fr'))

        return dict(
            format_currency=format_currency,
            format_percentage=format_percentage,
            now=datetime.utcnow,
            t=t,
            current_lang=getattr(g, 'lang', 'fr')
        )
    
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
