import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel, \
    QSizePolicy, QMessageBox
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtCore import Qt, QSortFilterProxyModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setGeometry(900, 400, 800, 800)

        # Создание виджетов
        self.search_label = QLabel("Поиск по заголовку:")
        self.table_label = QLabel("Таблица:")

        self.table_view = QTableView()  # для отображения записей из бд
        self.search_field = QLineEdit()  # поле для ввода текста

        self.refresh_button = QPushButton("Обновить")
        self.add_button = QPushButton("Добавить")
        self.delete_button = QPushButton("Удалить")

        # Компоновка
        layout = QVBoxLayout()

        layout.addWidget(self.search_label)
        layout.addWidget(self.search_field)

        layout.addWidget(self.table_label)

        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table_view)

        layout.addWidget(self.refresh_button)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.refresh_button.clicked.connect(self.refresh_data)
        self.add_button.clicked.connect(self.open_add_record_window)
        self.delete_button.clicked.connect(self.open_delete_record_window)

        self.init_db()

    def init_db(self):
        # Подключение к базе данных
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('posts.db')

        if not self.db.open():
            print("Ошибка при подключении к базе данных")
            return

        # Создание модели данных
        self.model = QSqlTableModel(self)
        self.model.setTable('posts')
        self.model.select()

        # Установка заголовков столбцов
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "User ID")
        self.model.setHeaderData(2, Qt.Horizontal, "Title")
        self.model.setHeaderData(3, Qt.Horizontal, "Body")

        # Установка поиска
        self.proxy_model = QSortFilterProxyModel(self)  # Создание прокси-модели для фильтрации
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)  # Установка прокси-модели
        self.search_field.textChanged.connect(self.filter_data)  # Подключение поля поиска к фильтрации

    def filter_data(self):  # Обновляет фильтр по содержимому search_field
        search_text = self.search_field.text()

        self.proxy_model.setFilterKeyColumn(2)  # Установка Фильтра по Title
        self.proxy_model.setFilterRegExp(search_text)  # Фильтр - игнорирование регистра

    def refresh_data(self):  # Обновляет данные модели
        self.model.select()

    def open_add_record_window(self):  # открывает окно для добавления записей.
        add_record_window = AddRecordWindow(self)
        add_record_window.show()

    def open_delete_record_window(self):  # открывают окно для удаления записей.
        delete_record_window = DeleteRecordWindow(self)
        delete_record_window.show()


class AddRecordWindow(QMainWindow):  # Окно для добавления новой записи
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Добавить запись")

        # Создание виджетов
        self.user_id_label = QLabel("User ID:")
        self.user_id_input = QLineEdit()

        self.title_label = QLabel("Title:")
        self.title_input = QLineEdit()

        self.body_label = QLabel("Body:")
        self.body_input = QLineEdit()

        self.add_button = QPushButton("Добавить")

        # Компоновка
        layout = QVBoxLayout()

        layout.addWidget(self.user_id_label)
        layout.addWidget(self.user_id_input)

        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)

        layout.addWidget(self.body_label)
        layout.addWidget(self.body_input)

        layout.addWidget(self.add_button)

        self.setLayout(layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.add_button.clicked.connect(self.add_record)

    def add_record(self):
        user_id = self.user_id_input.text()
        title = self.title_input.text()
        body = self.body_input.text()

        if user_id and title and body:
            # Проверка на тип число
            if not user_id.isdigit():
                QMessageBox.warning(self, "Ошибка", "User ID должен быть числом")
                return

            # Формирование SQL-запроса
            query = QSqlQuery()
            query.prepare("INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)")
            query.addBindValue(user_id)
            query.addBindValue(title)
            query.addBindValue(body)

            # Выполнение запроса и проверка на ошибки
            if not query.exec_():
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить запись")
            else:
                QMessageBox.information(self, "Успех", "Запись успешно добавлена")
                self.parent().refresh_data()
                self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")


class DeleteRecordWindow(QMainWindow):  # Окно для удаления записи по ID
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Удалить запись")

        # Создание виджетов
        self.id_label = QLabel("ID:")
        self.id_input = QLineEdit()

        self.delete_button = QPushButton("Удалить")

        # Компоновка
        layout = QVBoxLayout()

        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        layout.addWidget(self.delete_button)

        self.setLayout(layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.delete_button.clicked.connect(self.delete_record)

    def delete_record(self):
        id = self.id_input.text()

        if id:
            # Проверка на тип число
            if not id.isdigit():
                QMessageBox.warning(self, "Ошибка", "ID должен быть числом")
                return

            # Формирование SQL-запроса
            query = QSqlQuery()
            query.prepare(f"DELETE FROM posts WHERE id = {id}")

            # Выполнение запроса и проверка на ошибки
            if not query.exec_():
                QMessageBox.warning(self, "Ошибка", f"Запись {id} не удалена")
            else:
                QMessageBox.information(self, "Успех", f"Запись {id} удалена")
                self.parent().refresh_data()
                self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
