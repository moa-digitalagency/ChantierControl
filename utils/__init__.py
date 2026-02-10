import os
import uuid
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
        return Markup("0 MAD")

    formatted_value = f"{value:,.2f}".replace(',', ' ')

    # If the value is large (>= 100,000), reduce font size and break the currency to the next line
    if value >= 100000:
        return Markup(f"<span class='text-lg tracking-tight font-bold'>{formatted_value}</span><br><span class='text-xs text-gray-500 font-normal'>MAD</span>")

    return Markup(f"{formatted_value} MAD")

def format_percentage(value):
    if value is None:
        return "0%"
    return f"{value:.1f}%"
