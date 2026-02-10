from flask import Blueprint, render_template
from security import direction_required

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

@finance_bp.route('/')
@direction_required
def index():
    return render_template('finance/index.html')
