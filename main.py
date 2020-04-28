import requests
import os
from dotenv import load_dotenv
import random

DIRECTORY = 'files'
URL_LAST_COMICS = "http://xkcd.com/info.0.json"
URl_COMICS = ["http://xkcd.com/", "/info.0.json"]
VK_API = "https://api.vk.com/method/"
VERSION = "5.103"
METHOD_GETWALL = "photos.getWallUploadServer"
METHOD_SAVEWALL = "photos.saveWallPhoto"
METHOD_POSTWALL = "wall.post"


def create_directory():
    os.makedirs(DIRECTORY, exist_ok=True)


def image_download(url, filename):
    file_path = os.path.join(DIRECTORY, filename)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def create_url(method):
    return "".join([VK_API, method])


def get_response(url, payload=None):
    try:
        if payload:
            response = requests.get(url, params=payload)
        else:
            response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(f"Not possible to get response: {error}")
    else:
        return response.json()


def post_to_vk(url, payload):
    try:
        response = requests.post(url, params=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(f"Not possible to post data: {error}")
    else:
        return response.json()


def get_comics_details(url):
    create_directory()
    comics = get_response(url)
    comics_title = comics['safe_title'].replace(' ', '_').lower()
    filename = "".join([comics_title, os.path.splitext(comics['img'])[1]])
    image_download(comics['img'], filename)
    return comics['alt']


def upload_photo_on_wall(url, filename):
    with open(filename, 'rb') as file:
        files = {'photo': file}
        response = requests.post(url, files=files)
        response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    last_comics = get_response(URL_LAST_COMICS)['num']
    comics_id = random.randint(1, last_comics)
    url_comics_to_download = str(comics_id).join(URl_COMICS)
    comics_message = get_comics_details(url_comics_to_download)
    comics_filename = os.listdir(DIRECTORY)[0]

    load_dotenv()
    token = os.getenv("ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")
    payload_wall = {"access_token": token, "v": VERSION, "group_id": group_id}
    group_wall = get_response(create_url(METHOD_GETWALL), payload_wall)

    upload_url = group_wall['response']['upload_url']
    comics_file_path = os.path.join(DIRECTORY, comics_filename)
    photo_uploaded = upload_photo_on_wall(upload_url, comics_file_path)
    payload_saving = {
        "photo": photo_uploaded['photo'],
        "server": photo_uploaded['server'],
        "hash": photo_uploaded['hash'],
    }
    payload_saving.update(payload_wall)
    photo_saved = post_to_vk(create_url(METHOD_SAVEWALL), payload_saving)

    owner_id = str(photo_saved['response'][0]['owner_id'])
    media_id = str(photo_saved['response'][0]['id'])
    attachment = "".join(['photo', owner_id, '_', media_id])
    payload_wall_posting = {"attachments": attachment, "message": comics_message}
    payload_wall_posting.update(payload_wall)
    post_to_vk(create_url(METHOD_POSTWALL), payload_wall_posting)

    os.remove(comics_file_path)
