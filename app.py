# /var/www/html/app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
import uuid

# Название проекта
app = Flask("Lost and Found")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Создание папки
UPLOAD_FOLDER = 'static/uploads'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FULL_UPLOAD_FOLDER = os.path.join(BASE_DIR, UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = FULL_UPLOAD_FOLDER

# Формат файла
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)

# База данных
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<Item {self.name}>'
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Создает таблицы БД и папки uploads
@app.before_request
def create_tables_and_folders():
    with app.app_context():
        db.create_all()
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

# Стаус фото
@app.route('/')
def index():
    status_filter = request.args.get('filter')
    
    if status_filter and status_filter != 'Все':
        items = Item.query.filter_by(status=status_filter).all()
    else:
        items = Item.query.all()

    status_map = ['Найдено', 'Потеряно', 'Вернули владельцу']
    
    return render_template('index.html', 
                           items=items, 
                           status_map=status_map, 
                           current_filter=status_filter)

 # Получаем фото
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_name = request.form['name']
        item_description = request.form['description']
        item_status = request.form['status']
        image_filename = None

        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = str(uuid.uuid4()) + '.' + ext
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_filename = unique_filename

        new_item = Item(name=item_name, 
                        description=item_description, 
                        status=item_status, 
                        image_filename=image_filename)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('add.html')

# Настройка 
if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')
