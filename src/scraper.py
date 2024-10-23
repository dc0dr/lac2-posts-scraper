import os
import time
import re
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd 
from dotenv import load_dotenv

load_dotenv()

class PostScraper:
    
    def scrape_and_export():
        # Path to Edge webdriver and LinkedIn page
        edge_driver_path = "C:/WebDrivers/Edge/msedgedriver.exe"
        lac2_page_url = "https://www.linkedin.com/company/lac2/posts/?feedView=all"

        username = os.getenv('EMAIL') 
        password = os.getenv('PASSWORD')

        edge_options = Options()
        edge_options.add_argument('start-maximized')

        # Edge webdriver setup
        edge_service = Service(edge_driver_path)
        driver = webdriver.Edge(options=edge_options, service=edge_service)

        driver.get('https://www.linkedin.com/login')
        time.sleep(2)

        driver.find_element(By.ID, 'username').send_keys(username)
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.XPATH, '//*[@type="submit"]').click()
        time.sleep(3)

        # Navigate to the LinkedIn page
        driver.get(lac2_page_url)

        # Set parameters for scrolling through the page
        SCROLL_PAUSE_TIME = 1.5
        MAX_SCROLLS = False
        last_height = driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        no_change_count = 0

        # Scroll through the page until no new content is loaded
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            no_change_count = no_change_count + 1 if new_height == last_height else 0
            if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
                break
            last_height = new_height
            scrolls += 1


        # Extract the HTML content and parse the page with BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content.encode('utf-8'), 'html5lib')


        # with open('output.html', 'w', encoding='utf-8') as f:
        #     f.write(soup.prettify())
            
        driver.quit()


        # Extract post content
        posts = soup.find_all('span', {'class': 'break-words tvm-parent-container'})

        # Use regex to find all occurrences of 'urn:li:activity' and 'urn:li:ugcPost'
        post_links = []
        pattern = re.compile(r'urn:li:(activity|ugcPost):[0-9]+')

        # Search the entire HTML text for matching URNs
        urns = pattern.findall(html_content)

        # Build the post links, using a set to avoid duplicates
        unique_links = set()
        for urn in pattern.finditer(html_content):
            urn_text = urn.group()
            if 'urn:li:activity:' in urn_text:
                post_id = urn_text.split('urn:li:activity:')[-1]
                unique_links.add(f"https://www.linkedin.com/feed/update/urn:li:activity:{post_id}")
            elif 'urn:li:ugcPost:' in urn_text:
                post_id = urn_text.split('urn:li:ugcPost:')[-1]
                unique_links.add(f"https://www.linkedin.com/feed/update/urn:li:ugcPost:{post_id}")

        # Convert the set back to a list and sort it (optional)
        post_links = list(unique_links)

        # Categorize posts
        ai_events_links = []
        ai_breakfasts_links = []
        ai_interviews_links = []
        uncategorized = []

        for post, link in zip(posts, post_links):
            try:
                content = post.get_text(strip=True).lower()  # Lowercase for case-insensitive matching

                # Initialize flags
                is_event = False
                is_breakfast = False
                is_interview = False

                # Match and categorize based on keywords
                if re.search(r'\bbreakfast\b', content):
                    ai_breakfasts_links.append(link)
                    is_breakfast = True
                else:
                    ai_breakfasts_links.append('')

                if re.search(r'\b(interview|conversation)\b', content):
                    ai_interviews_links.append(link)
                    is_interview = True
                else:
                    ai_interviews_links.append('')

                # Handle events last, as it's a broader category
                if re.search(r'\b(event|conference|summit)\b', content):
                    ai_events_links.append(link)
                    is_event = True
                else:
                    ai_events_links.append('')

                # If none of the above categories matched, put in uncategorized
                if not is_event and not is_breakfast and not is_interview:
                    uncategorized.append(link)
                else:
                    uncategorized.append('')

            except Exception as e:
                print(f"Error parsing post: {e}")

        # Create a DataFrame to store categorized data
        df = pd.DataFrame({
            'AI Industry Events': ai_events_links,
            'AI Breakfasts': ai_breakfasts_links,
            'AI Interviews': ai_interviews_links,
            'Uncategorized': uncategorized
        })

        # Export to Excel
        df.to_excel('files\\LAC2 LinkedIn Posts.xlsx', index=False)

