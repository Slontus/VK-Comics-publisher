import requests
import os
from dotenv import load_dotenv
import random
import logging

logging.basicConfig(format="[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s",
                    level=logging.DEBUG, filename='log.log')
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
    try:
        response = requests.get(url)
    except requests.exceptions.HTTPError as error:
        logging.error(f"Not possible to download image: {error}")
    else:
        with open(file_path, 'wb') as _file:
            _file.write(response.content)


def create_url(method):
    return "".join([VK_API, method])


def get_response(url, payload=None):
    try:
        if payload:
            response = requests.get(url, params=payload)
            response.raise_for_status()
            confirmation = response.json()
            if 'error' in confirmation:
                raise requests.exceptions.HTTPError(confirmation['error'])
        else:
            response = requests.get(url)
            response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        logging.error(f"Not possible to get response: {error}")
    else:
        return response.json()


def post_to_vk(url, payload):
    try:
        response = requests.post(url, params=payload)
        response.raise_for_status()
        confirmation = response.json()
        if 'error' in confirmation:
            raise requests.exceptions.HTTPError(confirmation['error'])
    except requests.exceptions.HTTPError as error:
        logging.error(f"Not possible to post data: {error}")
    else:
        return confirmation


def download_comics(_comics):
    create_directory()
    comics_title = _comics['safe_title'].replace(' ', '_').lower()
    filename = "".join([comics_title, os.path.splitext(_comics['img'])[1]])
    image_download(_comics['img'], filename)


def upload_photo_on_wall(url, filename):
    try:
        with open(filename, 'rb') as _file:
            _files = {'photo': _file}
            response = requests.post(url, files=_files)
            response.raise_for_status()
    except requests.exceptions.InvalidSchema as error:
        logging.error(f"Not possible to upload file {filename} on wall: {error}")
    except FileNotFoundError:
        logging.error(f"File {filename} does not exist")
    else:
        return response.json()


if __name__ == "__main__":
    try:
        last_comics = get_response(URL_LAST_COMICS)['num']
        comics_id = random.randint(1, last_comics)
        url_comics_to_download = str(comics_id).join(URl_COMICS)
        comics = get_response(url_comics_to_download)
        download_comics(comics)
        comics_message = comics['alt']
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
    finally:
        files = os.listdir(DIRECTORY)
        for file in files:
            os.remove(os.path.join(DIRECTORY, file))
        logging.info("Temporary files removed from folder")
