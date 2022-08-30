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
    with open(file_name, 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
    response.raise_for_status()
    server_answer = response.json()
    return (
        server_answer['photo'],
        server_answer['server'],
        server_answer['hash']
        )


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
    save_comic = response.json()['response'][0]
    return save_comic['owner_id'], save_comic['id']


def get_comic(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['img'], response.json()['alt']


def main():
    try:
        load_dotenv()
        vk_token = os.environ['VK_TOKEN']
        version = 5.131
        group_id = os.environ['GROUP_ID']
        file_name = 'file.png'
        comics_amount = get_last_comic_issue()
        comic_number = random.randint(0, comics_amount)
        image_url, image_alt = get_comic(comic_number)
        download_file(image_url, file_name)
        uploading_url = get_upload_url(vk_token, group_id, version)
        photo, server, server_hash = upload_file(file_name, uploading_url)
        owner_id, media_id = save_comic(
            vk_token,
            group_id,
            version,
            photo,
            server,
            server_hash
        )
        post_comic(
            group_id,
            image_alt,
            owner_id,
            media_id,
            vk_token,
            version
        )
    finally:
        os.remove(file_name)


if __name__ == '__main__':
    main()
