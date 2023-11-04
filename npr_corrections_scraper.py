import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
import feedparser
import pytz

# URL to scrape
URL = 'https://www.npr.org/corrections/'

# Fetch the page
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize FeedGenerator
fg = FeedGenerator()
fg.id(URL)
fg.title('NPR Corrector Bot')
fg.author({'name': 'NPR', 'email': 'hmorris@npr.org'})
fg.link(href=URL, rel='alternate')
fg.subtitle('Corrections from NPR')
fg.language('en')
fg.lastBuildDate(datetime.utcnow().replace(tzinfo=pytz.utc))

# 1. Parse new corrections
new_entries = []

for correction in soup.find_all('div', class_='item-info')[:60]:
    title_link = correction.find('h2', class_='title').find('a')
    story_title = title_link.text.strip()
    story_link = title_link['href']
    correction_content_div = correction.find('div', class_='correction-content')
    correction_texts = [p.text for p in correction_content_div.find_all('p')]
    correction_text = "\n\n".join(correction_texts).strip()

    new_entries.append({
        'title': story_title,
        'link': story_link,
        'description': correction_text,
        'published': datetime.utcnow().timestamp()  # Current time as timestamp
    })

# 2. Read old entries from the existing RSS feed file
old_feed_entries = []

if os.path.exists('npr_corrections_rss.xml'):
    old_feed = feedparser.parse('npr_corrections_rss.xml')
    for entry in old_feed.entries:
        # Convert the string date to a datetime object and then to a timestamp for sorting
        published_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        old_feed_entries.append({
            'title': entry.title,
            'link': entry.link,
            'description': entry.description,
            'published': published_date.timestamp()
        })

existing_links = {entry['link'] for entry in old_feed_entries}

# 3. Process and add the new entries to a combined list
combined_entries = new_entries + [entry for entry in old_feed_entries if entry['link'] not in existing_links]

# Sort combined_entries in reverse chronological order based on the 'published' key
combined_entries.sort(key=lambda x: x['published'], reverse=True)

# Limit to 60 entries
combined_entries = combined_entries[:60]

# Add entries to the FeedGenerator
for entry_data in combined_entries:
    entry = fg.add_entry()
    entry.title(entry_data['title'])
    entry.link(href=entry_data['link'], rel='alternate')
    entry.description(entry_data['description'])
    entry.published(datetime.utcfromtimestamp(entry_data['published']).replace(tzinfo=pytz.utc).isoformat())

# Generate RSS feed
rssfeed = fg.rss_str(pretty=True)

# Write the RSS feed to a file
with open('npr_corrections_rss.xml', 'wb') as f:
    f.write(rssfeed)

print("RSS feed generated and saved as 'npr_corrections_rss.xml'")
