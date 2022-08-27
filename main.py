import requests
import os
import random
from dotenv import load_dotenv


def download_file(url, params, path):
    response = requests.get(url, params=params)
    with open(path, 'wb') as file:
        file.write(response.content)


def get_last_comic_issue():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['num']


def get_upload_url():
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


if __name__ == '__main__':
    load_dotenv()
    vk_token = os.environ['VK_TOKEN']
    version = 5.131
    group_id = os.environ['GROUP_ID']
    comics_amount = get_last_comic_issue()
    comic_number = random.randint(0, comics_amount)
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    about_comic = response.json()
    image_url = about_comic['img']
    download_file(image_url, {}, 'file.png')
    upload_url = get_upload_url()
    with open('file.png', 'rb') as file:
        files = {
            'photo': file
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        about_upload_photo = response.json()
    os.remove('file.png')
    payload = {
        'access_token': vk_token,
        'group_id': group_id,
        'v': version,
        'photo': about_upload_photo['photo'],
        'server': about_upload_photo['server'],
        'hash': about_upload_photo['hash']
    }
    response = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params=payload
    )
    response.raise_for_status()
    about_image = response.json()['response'][0]
    owner_id = about_image['owner_id']
    media_id = about_image['id']
    payload = {
        'owner_id': f'-{group_id}',
        'message': about_comic['alt'],
        'attachments': f'photo{owner_id}_{media_id}',
        'access_token': vk_token,
        'v': version
    }
    response = requests.post(
        'https://api.vk.com/method/wall.post',
        params=payload)
    response.raise_for_status()
