from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, flash

def hash_pin(pin):
    return generate_password_hash(str(pin))

def verify_pin(pin_hash, pin):
    return check_password_hash(pin_hash, str(pin))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def direction_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'direction':
            flash('Accès non autorisé', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    from models import User, db
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None
