import requests
import json


# 1. GET - запрос: Получение постов с четными id
def get_even_posts():
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    posts = response.json()

    even_posts = [post for post in posts if post['userId'] % 2 == 0]
    print("Посты с четными userId:")
    print(json.dumps(even_posts, indent=4))


# 2. POST - запрос: Создание поста
def create_post():
    url = "https://jsonplaceholder.typicode.com/posts"
    new_post = {
        "title": "Test post",
        "body": "your advertisement could be here.",
        "userId": 1
    }

    response = requests.post(url, json=new_post)
    created_post = response.json()

    print("Созданный пост:")
    print(json.dumps(created_post, indent=4))


# 3. PUT - запрос: Обновление поста
def update_post(post_id):
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    updated_post = {
        "title": "Updented post",
        "body": "Your advertisement could be here.",
        "userId": 1
    }

    response = requests.put(url, json=updated_post)
    updated_post_response = response.json()

    print("Обновлённый пост:")
    print(json.dumps(updated_post_response, indent=4))


if __name__ == "__main__":
    get_even_posts()
    create_post()
    update_post(1)

