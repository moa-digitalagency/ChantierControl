import os
import uuid
from datetime import date, timedelta, datetime
from werkzeug.utils import secure_filename
from PIL import Image
import imghdr
from markupsafe import Markup

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_stream):
    header = file_stream.read(512)
    file_stream.seek(0)
    
    format_type = imghdr.what(None, header)
    if format_type not in ['png', 'jpeg', 'gif']:
        return False
    return True

def save_photo(file, upload_folder='static/uploads'):
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        return None
    
    if not validate_image(file.stream):
        return None
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, filename)
    
    os.makedirs(upload_folder, exist_ok=True)
    
    try:
        image = Image.open(file)
        
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            ext = 'jpg'
            filename = f"{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(upload_folder, filename)
        
        image.thumbnail((1200, 1200))
        image.save(filepath, quality=85, optimize=True)
        
        return filename
    except Exception:
        return None

def format_currency(value):
    if value is None:
        return Markup("0.00 MAD")

    formatted_value = f"{value:,.2f}".replace(',', ' ')

    # Return single line string with non-breaking space
    return Markup(f"{formatted_value}&nbsp;MAD")

def format_percentage(value):
    if value is None:
        return "0%"
    return f"{value:.1f}%"

def get_date_range(filter_type, custom_start=None, custom_end=None):
    today = date.today()
    start_date = today
    end_date = today + timedelta(days=1)

    if filter_type == 'day':
        start_date = today
        end_date = today + timedelta(days=1)
    elif filter_type == 'week':
        # Monday to Sunday
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=7)
    elif filter_type == 'month':
        start_date = today.replace(day=1)
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1)
    elif filter_type == 'year':
        start_date = date(today.year, 1, 1)
        end_date = today + timedelta(days=1)
    elif filter_type == 'custom':
        try:
            if custom_start:
                start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
            if custom_end:
                end_date = datetime.strptime(custom_end, '%Y-%m-%d').date() + timedelta(days=1)
            else:
                end_date = today + timedelta(days=1)
        except ValueError:
            pass

    return start_date, end_date
