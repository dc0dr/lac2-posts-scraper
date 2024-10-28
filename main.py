import os
from src.scraper import PostScraper
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('client_id')
CLIENT_SECRET = os.getenv('client_secret')
ACCESS_TOKEN = os.getenv('access_token')
ORGANIZATION_ID = os.getenv('org_id')


# Path to the Excel file
file_path = 'files\\LAC2_LinkedIn_Posts.xlsx'

# Keywords for categorizing posts
events_keywords = ['event', 'conference', 'summit', 'symposium', 'workshop']
breakfast_keywords = ['breakfast', 'morning session', 'brunch']
interview_keywords = ['interview', 'conversation', 'discussion', 'talk', 'chat']

# Lists to store new links
ai_events_links = []
ai_breakfasts_links = []
ai_interviews_links = []
uncategorized = []

if __name__ == "__main__":
    scraper = PostScraper()

    post_links = scraper.get_post_links(ACCESS_TOKEN, ORGANIZATION_ID)

    if post_links:
        extracted_links = scraper.extract_post_links(post_links)
        extracted_post_ids = scraper.extract_post_id(post_links)

    for post, id in zip(extracted_links, extracted_post_ids):
        post_content = scraper.get_post_content(ACCESS_TOKEN, id['id'])
        post_id = id['id']
        commentary = post_content['results'][post_id]['commentary']
        epoch_time = post_content['results'][post_id]['publishedAt']
        date_time = datetime.fromtimestamp(epoch_time / 1000).strftime('%Y-%m-%d')
        print(f'Post URL: {post["url"]}\n Published At: {date_time}')

        try:
            content = commentary.lower()
            
            # Categorize each post link based on keywords and post content
            if scraper.contains_keyword(content, breakfast_keywords):
                ai_breakfasts_links.append(f'HYPERLINK=("{post["url"]}", "{date_time}")')
                ai_events_links.append('')
                ai_interviews_links.append('')
                uncategorized.append('')
            elif scraper.contains_keyword(content, interview_keywords):
                ai_breakfasts_links.append('')
                ai_events_links.append('')
                ai_interviews_links.append(f'HYPERLINK=("{post["url"]}", "{date_time}")')
                uncategorized.append('')
            elif scraper.contains_keyword(content, events_keywords):
                ai_breakfasts_links.append('')
                ai_events_links.append(f'HYPERLINK=("{post["url"]}", "{date_time}")')
                ai_interviews_links.append('')
                uncategorized.append('')
            else:
                ai_breakfasts_links.append('')
                ai_events_links.append('')
                ai_interviews_links.append('')
                uncategorized.append(f'HYPERLINK=("{post["url"]}", "{date_time}")')   
        except Exception as e:
            print(f"Error parsing post: {e}")