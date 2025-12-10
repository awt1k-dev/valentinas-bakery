import sqlite3
from typing import List, Optional, Tuple, Any

# Определяем тип для удобства чтения
ProductRow = Tuple[int, str, str, str, str, int]

class Database:
    """
    Класс для управления базой данных SQLite для продуктов.
    """
    def __init__(self, database_path: str = "products.db"):
        # Изменено имя файла, чтобы оно соответствовало контексту (продукты)
        self.database_path = database_path
        self.create_table() # Гарантируем, что таблица создана при инициализации

    def _execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Cursor]:
        """
        Приватный метод для выполнения запросов с использованием контекстного менеджера.
        Автоматически обрабатывает соединение и курсор.
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return None

    def create_table(self):
        """
        Создает таблицу 'products', если она еще не существует.
        """
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            is_available INTEGER DEFAULT 1 
        )
        """
        self._execute_query(query)
        print("Таблица 'products' проверена/создана.")

    # --- CRUD ОПЕРАЦИИ ---

    def add_product(self, name: str, description: str, price: float, category: str) -> Optional[int]:
        """
        Добавляет новый продукт в базу данных. Возвращает ID нового продукта.
        """
        query = """
        INSERT INTO products (name, description, price, category) 
        VALUES (?, ?, ?, ?)
        """
        # Преобразование цены в float, чтобы соответствовать типу REAL в таблице
        cursor = self._execute_query(query, (name, description, float(price), category))
        if cursor:
            return cursor.lastrowid
        return None

    def get_all_products(self) -> List[ProductRow]:
        """
        Получает все продукты из базы данных.
        """
        query = "SELECT * FROM products"
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.row_factory = sqlite3.Row # Позволяет получать результаты как словари/объекты
                cursor = conn.cursor()
                cursor.execute(query)
                return [tuple(row) for row in cursor.fetchall()] # Возвращаем список кортежей
        except sqlite3.Error as e:
            print(f"Ошибка при получении всех продуктов: {e}")
            return []

    def get_product_by_id(self, product_id: int) -> Optional[ProductRow]:
        """
        Получает продукт по его ID.
        """
        query = "SELECT * FROM products WHERE id = ?"
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (product_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка при получении продукта по ID: {e}")
            return None

    def edit_product(self, product_id: int, **kwargs) -> bool:
        """
        Обновляет поля продукта. Использует **kwargs для динамического обновления.
        Например: db.edit_product(1, price=99.99, is_available=0)
        """
        if not kwargs:
            print("Нет полей для обновления.")
            return False

        set_clauses = []
        params = []
        
        # Определяем допустимые поля для обновления
        allowed_fields = ['name', 'description', 'price', 'category', 'is_available']
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            print("Недопустимые поля для обновления.")
            return False
            
        set_clause = ", ".join(set_clauses)
        query = f"UPDATE products SET {set_clause} WHERE id = ?"
        params.append(product_id)
        
        cursor = self._execute_query(query, tuple(params))
        return bool(cursor and cursor.rowcount > 0)

    def delete_product(self, product_id: int) -> bool:
        """
        Удаляет продукт по его ID.
        """
        query = "DELETE FROM products WHERE id = ?"
        cursor = self._execute_query(query, (product_id,))
        return bool(cursor and cursor.rowcount > 0)


if __name__ == '__main__':
    # --- ПРИМЕР ИСПОЛЬЗОВАНИЯ ---
    
    db = Database()
    
    print("\n--- Добавление продукта ---")
    product_id_1 = db.add_product("Ноутбук Pro", "Мощный ноутбук", 1250.00, "Электроника")
    product_id_2 = db.add_product("Кофеварка Арома", "Автоматическая кофеварка", 85.50, "Бытовая техника")
    print(f"Добавлен продукт с ID: {product_id_1}")

    print("\n--- Все продукты ---")
    all_products = db.get_all_products()
    for prod in all_products:
        print(prod)

    print("\n--- Обновление цены ---")
    success = db.edit_product(product_id_1, price=1199.99, is_available=0)
    print(f"Продукт 1 обновлен: {success}")

    print("\n--- Получение по ID ---")
    updated_product = db.get_product_by_id(product_id_1)
    print(updated_product)

    print("\n--- Удаление продукта ---")
    db.delete_product(product_id_2)
    print(f"Продукт 2 удален.")
    
    print("\n--- Все продукты после удаления ---")
    for prod in db.get_all_products():
        print(prod)