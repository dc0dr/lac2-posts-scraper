import re
import requests

FEED_CONTENT_API_URL='https://api.linkedin.com/rest/dmaFeedContentsExternal'
POSTS_API_URL='https://api.linkedin.com/rest/dmaPosts'

class PostScraper:

    def get_post_links(self, access_token, organization_id):
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

    def get_post_content(self, access_token, post_id):
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

    def extract_post_links(self, post_links):
        posts = post_links.get('elements', [])

        extracted_links = []

        for post in posts:
            post_url = f"https://www.linkedin.com/feed/update/{post['id']}"
            extracted_links.append({
                'url': post_url
            })
            
        return extracted_links

    def extract_post_id(self, post_links):
        post_ids = post_links.get('elements', [])
        extracted_post_ids = []

        for post in post_ids:
            post_id = post['id']
            extracted_post_ids.append({
                'id': post_id
            })

        return extracted_post_ids

    def contains_keyword(self, content, keywords):
        """checks if any keyword is present in the content"""
        pattern = '|'.join(rf'\b{k}\b' for k in keywords)
        return re.search(pattern, content, re.IGNORECASE)
    
