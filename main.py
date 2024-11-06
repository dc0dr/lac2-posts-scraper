import os
from src.scraper import PostScraper
from src.excel_filter import ExcelCategorizer
from src.post_descriptor import Summarizer
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
ai_events_descriptions = []
ai_breakfasts_links = []
ai_breakfasts_descriptions = []
ai_interviews_links = []
ai_interviews_descriptions = []
uncategorized = []
uncategorized_descriptions = []


if __name__ == "__main__":
    scraper = PostScraper()
    categorizer = ExcelCategorizer()
    summarizer = Summarizer()

    post_links = scraper.get_post_links(ACCESS_TOKEN, ORGANIZATION_ID)

    if post_links:
        extracted_links = scraper.extract_post_links(post_links)
        extracted_post_ids = scraper.extract_post_id(post_links)

    for post, id in zip(extracted_links, extracted_post_ids):
        
        post_content = scraper.get_post_content(ACCESS_TOKEN, id['id'])
        post_id = id['id']
        commentary = post_content['results'][post_id]['commentary']
        summary = summarizer.generate_summary(commentary)
        epoch_time = post_content['results'][post_id]['publishedAt']
        date_time = datetime.fromtimestamp(epoch_time / 1000).strftime('%Y-%m-%d')
        console.log(f'Post URL: {post["url"]}\nPublished At: {date_time}\nSummary: {summary}')

        try:
            content = commentary.lower()
            # summary = sanitize_for_excel(summary)
            
            # Categorize each post link based on keywords and post content
            if scraper.contains_keyword(content, breakfast_keywords):
                ai_breakfasts_links.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')
                ai_breakfasts_descriptions.append(summary)
                ai_events_links.append('')
                ai_events_descriptions.append('')
                ai_interviews_links.append('')
                ai_interviews_descriptions.append('')
                uncategorized.append('')
                uncategorized_descriptions.append('')
            elif scraper.contains_keyword(content, interview_keywords):
                ai_breakfasts_links.append('')
                ai_breakfasts_descriptions.append('')
                ai_events_links.append('')
                ai_events_descriptions.append('')
                ai_interviews_links.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')
                ai_interviews_descriptions.append(summary)
                uncategorized.append('')
                uncategorized_descriptions.append('')
            elif scraper.contains_keyword(content, events_keywords):
                ai_breakfasts_links.append('')
                ai_breakfasts_descriptions.append('')
                ai_events_links.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')
                ai_events_descriptions.append(summary)
                ai_interviews_links.append('')
                ai_interviews_descriptions.append('')
                uncategorized.append('')
                uncategorized_descriptions.append('')
            else:
                ai_breakfasts_links.append('')
                ai_breakfasts_descriptions.append('')
                ai_events_links.append('')
                ai_events_descriptions.append('')
                ai_interviews_links.append('')
                ai_interviews_descriptions.append('')
                uncategorized.append(f'=HYPERLINK("{post["url"]}", "{date_time}")')
                uncategorized_descriptions.append(summary)
        except Exception as e:
            console.log(f"Error parsing post: {e}")

    # Check if the Excel file already exists
    if os.path.exists(file_path):
        console.log('\nExcel file found. Updating the file...')
        existing_df = pd.read_excel(file_path)
    else:
        console.log('\nCreating new Excel file...')
        existing_df = pd.DataFrame(columns=[
            'AI Breakfasts', 'Description (Breakfasts)', 
            'AI Events', 'Description (AI Events)', 
            'AI Interviews', 'Description (AI Interviews)', 
            'Uncategorized', 'Description (Uncategorized)'
        ])

    # Filter out duplicates for each category
    filtered_ai_events_links = categorizer.filter_new_links(ai_events_links, existing_df['AI Events'].dropna().values)
    filtered_ai_events_descriptions = categorizer.filter_new_links(ai_events_descriptions, existing_df['Description (Breakfasts)'].dropna().values)
    filtered_ai_breakfasts_links = categorizer.filter_new_links(ai_breakfasts_links, existing_df['AI Breakfasts'].dropna().values)
    filtered_ai_breakfasts_descriptions = categorizer.filter_new_links(ai_breakfasts_descriptions, existing_df['Description (AI Events)'].dropna().values)
    filtered_ai_interviews_links = categorizer.filter_new_links(ai_interviews_links, existing_df['AI Interviews'].dropna().values)
    filtered_ai_interviews_descriptions = categorizer.filter_new_links(ai_interviews_descriptions, existing_df['Description (AI Interviews)'].dropna().values)
    filtered_uncategorized = categorizer.filter_new_links(uncategorized, existing_df['Uncategorized'].dropna().values)
    filtered_uncategorized_descriptions = categorizer.filter_new_links(uncategorized_descriptions, existing_df['Description (Uncategorized)'].dropna().values)
    
    # Fill in the missing values to make the lists equal in length
    max_length = max(len(filtered_ai_events_links), len(filtered_ai_breakfasts_links), 
                        len(filtered_ai_interviews_links), len(filtered_uncategorized))
    filtered_ai_events_links.extend([''] * (max_length - len(filtered_ai_events_links)))
    filtered_ai_events_descriptions.extend([''] * (max_length - len(filtered_ai_events_descriptions)))
    filtered_ai_breakfasts_links.extend([''] * (max_length - len(filtered_ai_breakfasts_links)))
    filtered_ai_breakfasts_descriptions.extend([''] * (max_length - len(filtered_ai_breakfasts_descriptions)))
    filtered_ai_interviews_links.extend([''] * (max_length - len(filtered_ai_interviews_links)))
    filtered_ai_interviews_descriptions.extend([''] * (max_length - len(filtered_ai_interviews_descriptions)))
    filtered_uncategorized.extend([''] * (max_length - len(filtered_uncategorized)))
    filtered_uncategorized_descriptions.extend([''] * (max_length - len(filtered_uncategorized_descriptions)))

    # Create the DataFrame with the updated format
    new_data = pd.DataFrame({
        'AI Breakfasts': filtered_ai_breakfasts_links,
        'Description (Breakfasts)': filtered_ai_breakfasts_descriptions,
        # 'Empty 1': [''] * max_length,  # Empty column
        'AI Events': filtered_ai_events_links,
        'Description (AI Events)': filtered_ai_events_descriptions,
        # 'Empty 2': [''] * max_length,  # Empty column
        'AI Interviews': filtered_ai_interviews_links,
        'Description (AI Interviews)': filtered_ai_interviews_descriptions,
        # 'Empty 3': [''] * max_length,  # Empty column
        'Uncategorized': filtered_uncategorized,
        'Description (Uncategorized)': filtered_uncategorized_descriptions
    })

    existing_df = existing_df.loc[~existing_df.index.duplicated(keep='first')]
    new_data = new_data.loc[~new_data.index.duplicated(keep='first')]

    # Append and save to excel file
    updated_df = pd.concat([existing_df, new_data], ignore_index=True)
    updated_df.to_excel(file_path, index=False, engine="xlsxwriter")

    console.log('Excel file updated successfully!')
    
    
                                        