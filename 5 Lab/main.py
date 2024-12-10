import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel, \
    QSizePolicy, QProgressBar
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QTimer, QThread, pyqtSignal, QObject

import requests

import time
from threading import Thread

import asyncio
import aiosqlite


# Асинхронный класс для работы с базой данных
class DatabaseWorker(QObject):
    progress = pyqtSignal(int)  # Сигнал для обновления прогресса
    finished = pyqtSignal()  # Сигнал для завершения работ
    error = pyqtSignal(str)  # Сигнал для обработки ошибок

    # Асинхронный метод для сохранения данных в базе
    async def save_to_db(self, posts):
        try:
            async with aiosqlite.connect('posts.db') as db:
                await db.execute(
                    'CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL)')
                total_posts = len(posts)
                for index, post in enumerate(posts):
                    await db.execute('INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)',
                                     (post['userId'], post['title'], post['body']))
                    self.progress.emit(int((index + 1) / total_posts * 100))  # Обновление прогресса
                    await asyncio.sleep(0.05)  # Имитация задержки
                await db.commit()  # Сохранение изменений в базе данных
        except Exception as e:
            self.error.emit(str(e))  # Отправка сообщения об ошибке
        finally:
            self.finished.emit()  # Отправка сигнала о завершении


# Поток для получения данных из API
class FetchDataThread(QThread):
    def __init__(self):
        super().__init__()
        self.worker = DatabaseWorker()

    def run(self):
        time.sleep(1)
        response = requests.get('https://jsonplaceholder.typicode.com/posts')
        posts = response.json()
        asyncio.run(self.worker.save_to_db(posts))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setGeometry(900, 400, 800, 800)

        self.thread = FetchDataThread()
        self.thread.worker.progress.connect(self.update_progress)
        self.thread.worker.finished.connect(self.on_finished)
        self.thread.worker.error.connect(self.on_error)

        # Создание виджетов
        self.search_label = QLabel("Поиск по заголовку (Title):")
        self.table_label = QLabel("Таблица:")

        self.table_view = QTableView()
        self.search_field = QLineEdit()

        self.progressBar = QProgressBar()
        self.button = QPushButton('Загрузить данные')
        self.button.clicked.connect(self.start_fetch_data)

        # Компоновка
        layout = QVBoxLayout()

        layout.addWidget(self.search_label)
        layout.addWidget(self.search_field)

        layout.addWidget(self.table_label)

        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table_view)

        layout.addWidget(self.progressBar)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.init_db()

        # Таймер для автоматической проверки данных
        self.timer_check_update = QTimer()
        self.timer_check_update.timeout.connect(self.update_time_check_update)
        self.timer_check_update.start(10000)

    # Автоматическая проверка данных
    def update_time_check_update(self):
        print("check update!")
        self.start_fetch_data()

    # Начало загрузки данных в поток
    def start_fetch_data(self):
        if not self.thread.isRunning():
            self.progressBar.setValue(0)
            self.thread.start()

    # Обновление прогресса
    def update_progress(self, value):
        self.progressBar.setValue(value)

    # Действие по завершению работы
    def on_finished(self):
        print("Data saved successfully.")
        self.refresh_data()

    # Действие при ошибке
    def on_error(self, error_message):
        print(f"An error occurred: {error_message}")

    # Инициализация базы данных и модели данных
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

    # Фильтрация данных по тексту
    def filter_data(self):
        search_text = self.search_field.text()

        self.proxy_model.setFilterKeyColumn(2)  # Установка Фильтра по Title
        self.proxy_model.setFilterRegExp(search_text)  # Фильтр - игнорирование регистра

    # Обновление отображения данных
    def refresh_data(self):
        self.model.select()


# Запуск
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())