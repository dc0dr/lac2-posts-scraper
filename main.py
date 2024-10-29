import os
from src.scraper import PostScraper
from src.excel_filter import ExcelCategorizer
from datetime import datetime
import pandas as pd
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()

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
    categorizer = ExcelCategorizer()

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
        console.log(f'Post URL: {post["url"]}\nPublished At: {date_time}')

        try:
            content = commentary.lower()
            
            # Categorize each post link based on keywords and post content
            if scraper.contains_keyword(content, breakfast_keywords):
                ai_breakfasts_links.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')
                ai_events_links.append('')
                ai_interviews_links.append('')
                uncategorized.append('')
            elif scraper.contains_keyword(content, interview_keywords):
                ai_breakfasts_links.append('')
                ai_events_links.append('')
                ai_interviews_links.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')
                uncategorized.append('')
            elif scraper.contains_keyword(content, events_keywords):
                ai_breakfasts_links.append('')
                ai_events_links.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')
                ai_interviews_links.append('')
                uncategorized.append('')
            else:
                ai_breakfasts_links.append('')
                ai_events_links.append('')
                ai_interviews_links.append('')
                uncategorized.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')   
        except Exception as e:
            console.log(f"Error parsing post: {e}")

    # Check if the Excel file already exists
    if os.path.exists(file_path):
        console.log('\nExcel file found. Updating the file...')
        existing_df = pd.read_excel(file_path)
    else:
        console.log('\nCreating new Excel file...')
        existing_df = pd.DataFrame(columns=['AI Breakfasts', 'AI Events', 'AI Interviews', 'Uncategorized'])

    # Filter out duplicates for each category
    filtered_ai_events_links = categorizer.filter_new_links(ai_events_links, existing_df['AI Events'].dropna().values)
    filtered_ai_breakfasts_links = categorizer.filter_new_links(ai_breakfasts_links, existing_df['AI Breakfasts'].dropna().values)
    filtered_ai_interviews_links = categorizer.filter_new_links(ai_interviews_links, existing_df['AI Interviews'].dropna().values)
    filtered_uncategorized = categorizer.filter_new_links(uncategorized, existing_df['Uncategorized'].dropna().values)

    # Fill in the missing values to make the lists equal in length
    max_length = max(len(filtered_ai_events_links), len(filtered_ai_breakfasts_links), 
                     len(filtered_ai_interviews_links), len(filtered_uncategorized))
    filtered_ai_events_links.extend([''] * (max_length - len(filtered_ai_events_links)))
    filtered_ai_breakfasts_links.extend([''] * (max_length - len(filtered_ai_breakfasts_links)))
    filtered_ai_interviews_links.extend([''] * (max_length - len(filtered_ai_interviews_links)))
    filtered_uncategorized.extend([''] * (max_length - len(filtered_uncategorized)))

    new_data = pd.DataFrame({
        'AI Breakfasts': filtered_ai_breakfasts_links,
        'AI Events': filtered_ai_events_links,
        'AI Interviews': filtered_ai_interviews_links,
        'Uncategorized': filtered_uncategorized
    })

    updated_df = pd.concat([existing_df, new_data], ignore_index=True)
    updated_df.to_excel(file_path, index=False, engine="xlsxwriter")

    console.log('Excel file updated successfully!')
    
    
                                        