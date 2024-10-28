import os
import time
import re
import pandas as pd 
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('client_id')
CLIENT_SECRET = os.getenv('client_secret')
REDIRECT_URI = os.getenv('redirect_uri')
ACCESS_TOKEN = os.getenv('access_token')
ORGANIZATION_ID = os.getenv('org_id')

FEED_CONTENT_API_URL='https://api.linkedin.com/rest/dmaFeedContentsExternal'
POSTS_API_URL='https://api.linkedin.com/rest/dmaPosts'

class PostScraper:
    
    file_path = 'files\\LAC2_LinkedIn_Posts.xlsx'

    def get_post_links(access_token, organization_id):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'LinkedIn-Version': '202408'
        }

        params = {
            'author': f'urn:li:organization:{organization_id}',
            'maxPaginationCount': '20',
            'q': 'postsByAuthor'
        }

        response = requests.get(FEED_CONTENT_API_URL, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve post links:", f"{response.json().get('message')}.", "Status code:", response.status_code)
            return None

    def get_post_content(access_token, post_id):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'LinkedIn-Version': '202408'
        }

        params = {
            'ids': f'{post_id}'
        }

        response = requests.get(POSTS_API_URL, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve post content:", f"{response.json().get('message')}.", "Status code:", response.status_code)
            return None

    def extract_post_links(post_links):
        posts = post_links.get('elements', [])

        extracted_links = []

        for post in posts:
            post_url = f"https://www.linkedin.com/feed/update/{post['id']}"
            extracted_links.append({
                'url': post_url
            })
            
        return extracted_links

    def extract_post_id(post_links):
        post_ids = post_links.get('elements', [])
        extracted_post_ids = []

        for post in post_ids:
            post_id = post['id']
            extracted_post_ids.append({
                'id': post_id
            })

        return extracted_post_ids

    post_links = get_post_links(ACCESS_TOKEN, ORGANIZATION_ID)

    
    if post_links:
        extracted_links = extract_post_links(post_links)
        extracted_post_ids = extract_post_id(post_links)

    for post, id in zip(extracted_links, extracted_post_ids):
        post_content = get_post_content(ACCESS_TOKEN, id['id'])
        post_id = id['id']
        commentary = post_content['results'][post_id]['commentary']

        print(f'Post URL: {post["url"]}')