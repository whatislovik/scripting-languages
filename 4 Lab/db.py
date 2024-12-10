import sqlite3
import requests

# Создание базы данных
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL
)
''')

conn.commit()
conn.close()

# GET-запрос и запись данных в БД
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
url = "https://jsonplaceholder.typicode.com/posts"

response = requests.get(url)
posts = response.json()
posts_users = [post for post in posts if post['userId'] % 2 == 0]

for post in posts_users:
    print(post)
    cursor.execute('''
    INSERT INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)
    ''', (post['id'], post['userId'], post['title'], post['body']))

conn.commit()
conn.close()

# Чтение всех данных из БД
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM posts')
rows = cursor.fetchall()

for row in rows:
    post_id, user_id, title, body = row
    print(f"Post ID: {post_id}")
    print(f"User ID: {user_id}")
    print(f"Title: {title}")
    print(f"Body: {body}")
    print("-" * 40)

conn.close()

# Чтение данных из БД по id пользователя
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()
id = 2
cursor.execute(f"SELECT * FROM posts WHERE user_id ={id}")
rows = cursor.fetchall()

for row in rows:
    post_id, user_id, title, body = row
    print(f"Post ID: {post_id}")
    print(f"User ID: {user_id}")
    print(f"Title: {title}")
    print(f"Body: {body}")
    print("-" * 40)

conn.close()