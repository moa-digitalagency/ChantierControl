import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(file, upload_folder='static/uploads'):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(upload_folder, filename)
        
        os.makedirs(upload_folder, exist_ok=True)
        
        image = Image.open(file)
        image.thumbnail((1200, 1200))
        image.save(filepath, quality=85, optimize=True)
        
        return filename
    return None

def format_currency(value):
    if value is None:
        return "0 MAD"
    return f"{value:,.2f} MAD".replace(',', ' ')

def format_percentage(value):
    if value is None:
        return "0%"
    return f"{value:.1f}%"
