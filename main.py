import requests
import os
import random
from dotenv import load_dotenv


def download_file(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


def upload_file(file_name, upload_url):
    try:
        with open(file_name, 'rb') as file:
            files = {
                'photo': file
            }
            response = requests.post(upload_url, files=files)
        response.raise_for_status()
        return response.json()
    finally:
        os.remove(file_name)


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


def post_comic(group_id, text, owner_id, media_id, vk_token, version):
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


def save_comic(vk_token, group_id, version, photo, server, server_hash):
    payload = {
        'access_token': vk_token,
        'group_id': group_id,
        'v': version,
        'photo': photo,
        'server': server,
        'hash': server_hash
    }
    response = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params=payload
    )
    response.raise_for_status()
    return response.json()['response'][0]


def get_comic(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def main():
    load_dotenv()
    vk_token = os.environ['VK_TOKEN']
    version = 5.131
    group_id = os.environ['GROUP_ID']
    file_name = 'file.png'
    comics_amount = get_last_comic_issue()
    comic_number = random.randint(0, comics_amount)
    received_comic = get_comic(comic_number)
    image_url = received_comic['img']
    download_file(image_url, file_name)
    upload_url = get_upload_url(vk_token, group_id, version)
    upload_comic = upload_file(file_name, upload_url)
    about_save_comic = save_comic(
        vk_token,
        group_id,
        version,
        upload_comic['photo'],
        upload_comic['server'],
        upload_comic['hash']
    )
    post_comic(
        group_id,
        received_comic['alt'],
        about_save_comic['owner_id'],
        about_save_comic['id'],
        vk_token,
        version
    )


if __name__ == '__main__':
    main()