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
tech_talks_keywords = ['tech talks', 'tech talk', 'tech session', 'tech discussion', 'tech chat']

# Lists to store new links
dates = []
descriptions = []
categories = []
links = []


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
        summary = summary.strip('"')
        epoch_time = post_content['results'][post_id]['publishedAt']
        date_time = datetime.fromtimestamp(epoch_time / 1000).strftime('%Y-%m-%d')
        # console.log(f'Post URL: {post["url"]}\nPublished At: {date_time}\nSummary: {summary}')

        try:
            content = commentary.lower()
            # summary = sanitize_for_excel(summary)
            
            # Categorize each post link based on keywords and post content
            if scraper.contains_keyword(content, breakfast_keywords):
                category = "AI Breakfast"
            elif scraper.contains_keyword(content, interview_keywords):
                category = "AI Interview"
            elif scraper.contains_keyword(content, events_keywords):
                category = "AI Event"
            elif scraper.contains_keyword(content, tech_talks_keywords):
                category = "Tech Talks"
            else:
                category = "Uncategorized"

            # Append data to lists
            dates.append(date_time)
            descriptions.append(summary)
            categories.append(category)
            links.append(post["url"])

            console.log(f'Post URL: {post["url"]}\nDate: {date_time}\nCategory: {category}\nSummary: {summary}')
            
        except Exception as e:
            console.log(f"Error parsing post: {e}")

    # Create new DataFrame with the new structure
    new_data = pd.DataFrame({
        'Date': dates,
        'Event Description (Generated with AI)': descriptions,
        'Category': categories,
        'Link to Post': links
    })

    # Check if the Excel file already exists
    if os.path.exists(file_path):
        console.log('\nExcel file found. Updating the file...')
        existing_df = pd.read_excel(file_path)

        existing_links = set(existing_df['Link to Post'].dropna().values)

        new_data = new_data[~new_data['Link to Post'].isin(existing_links)]

        updated_df = pd.concat([existing_df, new_data], axis=0)
    else:
        console.log('\nCreating new Excel file...')
        updated_df = new_data


    updated_df['Date'] = pd.to_datetime(updated_df['Date']).dt.strftime('%Y-%m-%d')
    updated_df = updated_df.sort_values(by='Date', ascending=False)
    updated_df = updated_df.drop_duplicates(subset='Link to Post', keep='first')

    updated_df['Link to Post'] = updated_df.apply(
        lambda row: f'=HYPERLINK("{row["Link to Post"]}")',
        axis=1
    )

    # Save to Excel
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        updated_df.to_excel(writer, index=False, sheet_name='Posts Sheet')

        # Auto-adjust colunm widths
        worksheet = writer.sheets['Posts Sheet']
        for idx, col in enumerate(updated_df.columns):
            series = updated_df[col]
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(series.name))
            )
            worksheet.set_column(idx, idx, max_len)

    console.log('Excel file updated successfully')
                                        