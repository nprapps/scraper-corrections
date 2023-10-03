import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import os
import feedparser

# Timezone adjustment
eastern_timezone = pytz.timezone('US/Eastern')
current_utc_time = datetime.now(pytz.utc)
current_et_time = current_utc_time.astimezone(eastern_timezone)

# URL to scrape
URL = 'https://www.npr.org/corrections/'

# Fetch the page
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# Check if the old RSS file exists and read its entries if it does
old_entries = {}
if os.path.exists('npr_corrections_rss.xml'):
    old_feed = feedparser.parse('npr_corrections_rss.xml')
    for entry in old_feed.entries:
        old_entries[entry.id] = entry.published

# Initialize FeedGenerator
fg = FeedGenerator()
fg.id(URL)
fg.title('NPR Corrections')
fg.author({'name': 'NPR', 'email': 'hmorris@npr.org'})
fg.link(href=URL, rel='alternate')
fg.subtitle('Corrections from NPR')
fg.language('en')
fg.lastBuildDate(current_et_time)

# Parse the corrections
corrections = soup.find_all('div', class_='item-info')
# ... (the rest of the imports and the beginning of your script remains unchanged)

for correction in reversed(corrections[:5]):
    entry = fg.add_entry()
        
    # Extracting title and link of the story
    title_link = correction.find('h2', class_='title').find('a')
    story_title = title_link.text.strip()
    story_link = title_link['href']
    
    # Extracting the correction details
    correction_content_div = correction.find('div', class_='correction-content')
    #corrected_on_text = correction_content_div.find('h3', class_='corrected-on').text.strip()
    #corrected_on_date_str = corrected_on_text.replace('Corrected on ', '')
    #corrected_on_date = datetime.strptime(corrected_on_date_str, '%Y-%m-%d %H:%M:%S')
    #formatted_date = corrected_on_date.strftime('%a, %d %b %Y %H:%M:%S -0500')  # RFC 822 format
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime('%a, %d %b %Y %H:%M:%S -0500')  # RFC 822 format

    correction_text = correction_content_div.find('p').text.strip()

    # Adding to the RSS feed entry
    entry.id(story_link)
    entry.title(f"{story_title}")
    entry.link(href=story_link, rel='alternate')
    # Check if this correction already exists in the old feed
    if story_link in old_entries:
        entry.published(old_entries[story_link])
    else:
        entry.published(formatted_date)
    description_content = f"{correction_text}"
    entry.description(description_content)


# Generate RSS feed
rssfeed = fg.rss_str(pretty=True)

# Write the RSS feed to a file
with open('npr_corrections_rss.xml', 'wb') as f:
#with open('/home/runner/work/corrections-scraper/corrections-scraper/npr_corrections_rss.xml', 'wb') as f:
    f.write(rssfeed)

print("RSS feed generated and saved as 'npr_corrections_rss.xml'")
