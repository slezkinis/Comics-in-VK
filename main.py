import requests
import os
import random
from dotenv import load_dotenv


def download_file(url, params, path):
    response = requests.get(url, params=params)
    with open(path, 'wb') as file:
        file.write(response.content)


def upload_file(file_name):
    with open(file_name, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    os.remove(file_name)
    return response.json()


def get_last_comic_issue():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def get_upload_url(vk_token, group_id, version):
    payload = {
        'access_token': vk_token,
        'group_id': group_id,
        'v': version
    }
    response = requests.post(
        'https://api.vk.com/method/photos.getWallUploadServer',
        params=payload
    )
    response.raise_for_status()
    return response.json()['response']['upload_url']


def public_photo(group_id, text, owner_id, media_id, vk_token, version):
    payload = {
        'owner_id': f'-{group_id}',
        'message': text,
        'attachments': f'photo{owner_id}_{media_id}',
        'access_token': vk_token,
        'v': version
    }
    response = requests.post(
        'https://api.vk.com/method/wall.post',
        params=payload)
    response.raise_for_status()


def save_wall_photo(vk_token, group_id, version, photo, server, hash):
    payload = {
        'access_token': vk_token,
        'group_id': group_id,
        'v': version,
        'photo': photo,
        'server': server,
        'hash': hash
    }
    response = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params=payload
    )
    response.raise_for_status()
    return response.json()['response'][0]


def get_comic_url(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    about_comic = response.json()
    return about_comic


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.environ['VK_TOKEN']
    version = 5.131
    group_id = os.environ['GROUP_ID']
    file_name = 'file.png'
    comics_amount = get_last_comic_issue()
    comic_number = random.randint(0, comics_amount)
    about_comic = get_comic_url(comic_number)
    image_url = about_comic['img']
    download_file(image_url, {}, file_name)
    upload_url = get_upload_url(vk_token, group_id, version)
    about_upload_photo = upload_file(file_name)
    about_image = save_wall_photo(
        vk_token,
        group_id,
        version,
        about_upload_photo['photo'],
        about_upload_photo['server'],
        about_upload_photo['hash']
    )
    public_photo(
        group_id,
        about_comic['alt'],
        about_image['owner_id'],
        about_image['id'],
        vk_token,
        version
    )
