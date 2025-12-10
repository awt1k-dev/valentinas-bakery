from flask import Flask, render_template, session, request, redirect, url_for, flash
from dotenv import load_dotenv
load_dotenv()
import os
from os import path
from werkzeug.utils import secure_filename
from datetime import timedelta
from database import Database

app = Flask(__name__)
app.secret_key = os.getenv("secret")
app.permanent_session_lifetime = timedelta(7)

database = Database()

# --- Конфигурация загрузки файлов ---
photo_formats = ['jpg', 'webp', 'png', 'jpeg']
# Ограничение размера файла до 10 МБ (10 * 1024 * 1024)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
# Папка для сохранения загруженных файлов (должна существовать: static/images/products)
UPLOAD_FOLDER = 'static/images/products'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ------------------------------------

# --- Вспомогательные функции ---

def allowed_file(filename):
    """Проверяет, разрешено ли расширение файла."""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in photo_formats

def find_product_photo(product_id):
    """Ищет существующее фото для продукта по ID и возвращает его URL."""
    for ext in photo_formats:
        photo_path = path.join(app.config['UPLOAD_FOLDER'], f"{product_id}.{ext}")
        # Проверяем наличие файла на диске
        if path.exists(photo_path):
            # Возвращаем URL для использования в HTML (например, /static/images/products/1.jpg)
            return url_for('static', filename=f'images/products/{product_id}.{ext}')
    return None

# Регистрация функции как глобальной переменной Jinja2 для использования в шаблонах
app.jinja_env.globals.update(find_product_photo=find_product_photo)


def admin_required():
    if 'login' not in session:
        flash("Требуется авторизация.", "error")
        return redirect(url_for('admin_login'))
    return None
# --------------------------------------------------------

##################################################################################
# Base Pages
##################################################################################

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/contacts')
def contacts():
    return render_template("contacts.html")

@app.route('/catalog')
def catalog():
    # Загружаем доступные продукты для каталога
    products_raw = database.get_all_products()
    
    # Обогащаем список продуктов путем к фото
    products_with_photos = []
    for product in products_raw:
        product_list = list(product) # Преобразование кортежа в список
        # product_list[0] - это ID продукта
        photo_url = find_product_photo(product_list[0])
        product_list.append(photo_url) # Добавляем URL фото как 7-й элемент
        products_with_photos.append(product_list)
        
    return render_template("catalog.html", products=products_with_photos)


##################################################################################
# Admin Panel - Core
##################################################################################

@app.route('/admin')
def admin():
    # Проверяем авторизацию и перенаправляем на панель
    auth_check = admin_required()
    if auth_check:
        return auth_check
    return redirect(url_for('admin_panel'))


@app.route('/admin/login', methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        login = request.form.get("login") 
        password = request.form.get("password")
        if login == os.getenv("admin-login") and password == os.getenv("admin-password"):
            session["login"] = os.getenv("admin-login")
            return redirect(url_for("admin_panel"))
        else:
            flash("Неверное имя пользователя или пароль!", "error")
            return redirect(url_for('admin_login'))
    return render_template("admin_login.html")


@app.route('/admin/panel')
def admin_panel():
    auth_check = admin_required()
    if auth_check:
        return auth_check

    # Получаем все продукты из БД
    products = database.get_all_products()
    return render_template("admin_panel.html", products=products)


@app.route('/admin/logout')
def admin_logout():
    session.pop('login', None)
    flash("Вы успешно вышли.", "success")
    return redirect(url_for('admin_login'))

##################################################################################
# Admin Panel - CRUD Operations
##################################################################################

@app.route('/admin/product/add', methods=['GET', 'POST'])
def add_product():
    auth_check = admin_required()
    if auth_check:
        return auth_check

    categories = ['Зефир', 'Букеты', 'Торты', 'Выпечка', 'Другое']

    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        
        if not name or not price:
            flash("Поля Название и Цена обязательны!", "error")
            return render_template('product_form.html', categories=categories, action='add', product=None)
        
        # 1. Добавляем продукт в БД и получаем ID
        product_id = database.add_product(name, description, price, category)
        
        if product_id:
            # 2. Обработка загрузки файла
            file = request.files.get('photo')
            
            if file and file.filename != '':
                if allowed_file(file.filename):
                    # Получаем безопасное имя файла (для расширения)
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    # Имя файла = ID продукта + расширение
                    filename = f"{product_id}.{ext}"
                    
                    # Сохраняем файл
                    file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
                    flash(f"Товар '{name}' и фото успешно добавлены!", "success")
                    return redirect(url_for('admin_panel'))
                else:
                    # Если файл не разрешен, удаляем запись из БД, чтобы избежать "сироты"
                    database.delete_product(product_id) 
                    flash("Недопустимый формат файла. Товар не добавлен. Допустимы: " + ", ".join(photo_formats), "error")
                    return redirect(url_for('add_product'))

            # Если фото не загружено
            flash(f"Товар '{name}' успешно добавлен (без фото).", "success")
            return redirect(url_for('admin_panel'))
        else:
            flash("Ошибка при добавлении товара в базу данных.", "error")

    return render_template('product_form.html', categories=categories, action='add', product=None)


@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    auth_check = admin_required()
    if auth_check:
        return auth_check

    # Получаем продукт по ID, чтобы заполнить форму
    product_tuple = database.get_product_by_id(product_id)
    if not product_tuple:
        flash("Товар не найден.", "error")
        return redirect(url_for('admin_panel'))
    
    # Преобразуем кортеж в словарь для удобства доступа
    product = {
        'id': product_tuple[0],
        'name': product_tuple[1],
        'description': product_tuple[2],
        'price': product_tuple[3],
        'category': product_tuple[4],
        'is_available': product_tuple[5]
    }

    categories = ['Зефир', 'Букеты', 'Торты', 'Выпечка', 'Другое']

    if request.method == 'POST':
        # Собираем данные для обновления
        update_data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'category': request.form.get('category'),
            'is_available': 1 if request.form.get('is_available') == 'on' else 0
        }
        
        photo_updated = False
        
        # 1. Обработка загрузки файла
        file = request.files.get('photo')
        
        if file and file.filename != '':
            if allowed_file(file.filename):
                
                # Удаляем старый файл (ищем среди всех разрешенных форматов)
                for ext in photo_formats:
                    old_path = path.join(app.config['UPLOAD_FOLDER'], f"{product_id}.{ext}")
                    if path.exists(old_path):
                        os.remove(old_path)
                        break
                
                # Сохраняем новый файл
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{product_id}.{ext}"
                file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_updated = True
            else:
                flash("Недопустимый формат файла. Обновление фото отменено, текстовые данные сохранены.", "error")
                # Здесь мы не прерываемся, чтобы обновить хотя бы текстовые поля
                
        # 2. Обновляем текстовые данные в БД
        success = database.edit_product(product_id, **update_data)
        
        if success:
            if photo_updated:
                 flash(f"Товар '{update_data['name']}' и фото успешно обновлены.", "success")
            else:
                 flash(f"Товар '{update_data['name']}' успешно обновлен.", "success")
                 
            return redirect(url_for('admin_panel'))
        else:
            flash("Ошибка при обновлении товара в базе данных.", "error")

    return render_template('product_form.html', product=product, categories=categories, action='edit')


@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    auth_check = admin_required()
    if auth_check:
        return auth_check

    # 1. Удаляем товар из database.py
    success = database.delete_product(product_id)
    
    if success:
        # 2. NEW: Удаление файла с диска
        photo_deleted = False
        for ext in photo_formats:
            photo_path = path.join(app.config['UPLOAD_FOLDER'], f"{product_id}.{ext}")
            if path.exists(photo_path):
                os.remove(photo_path)
                photo_deleted = True
                break
                
        flash(f"Товар с ID:{product_id} и {'его фото' if photo_deleted else 'без фото'} успешно удален.", "success")
    else:
        flash("Ошибка при удалении товара. Возможно, он не существует.", "error")
        
    return redirect(url_for('admin_panel'))


if __name__ == "__main__":
    # Убедитесь, что папка для загрузки существует
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Создана папка: {UPLOAD_FOLDER}")
        
    app.run(port=5000, debug=True)