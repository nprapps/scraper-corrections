import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz
import os
import feedparser
import json

# Timezone adjustment (this can be removed if you're not using it)
eastern_timezone = pytz.timezone('US/Eastern')
current_utc_time = datetime.now(pytz.utc)
current_et_time = current_utc_time.astimezone(eastern_timezone)

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
fg.lastBuildDate(current_utc_time)

# 1. Parse new corrections
new_entries = []

for correction in soup.find_all('div', class_='item-info',limit=10):
    title_link = correction.find('h2', class_='title').find('a')
    story_title = title_link.text.strip()
    story_link = title_link['href']
    correction_content_div = correction.find('div', class_='correction-content')
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime('%a, %d %b %Y %H:%M:%S +0000')
    correction_texts = [p.text for p in correction_content_div.find_all('p')]
    correction_text = "\n\n".join(correction_texts).strip()

    new_entries.append({
        'title': story_title,
        'link': story_link,
        'description': correction_text,
        'published': formatted_date
    })

# 2. Read old entries from the existing RSS feed file
old_feed_entries = []

if os.path.exists('npr_corrections_rss.xml'):
    old_feed = feedparser.parse('npr_corrections_rss.xml')
    for entry in old_feed.entries[:10]:
        old_feed_entries.append({
            'title': entry.title,
            'link': entry.link,
            'description': entry.description,
            'published': entry.published
        })

# Write new_entries to a file
#with open('new_entries.json', 'w', encoding='utf-8') as f:
#    json.dump(new_entries, f, ensure_ascii=False, indent=4)

# Write old_feed_entries to a file
#with open('old_feed_entries.json', 'w', encoding='utf-8') as f:
#    json.dump(old_feed_entries, f, ensure_ascii=False, indent=4)


# 3. Compare and Add Entries to the RSS Feed

old_identifiers = [(entry['link']) for entry in old_feed_entries]

# First, add entries that are NEW (not in the old feed)
for entry_data in reversed(new_entries):
    identifier = (entry_data['link'])
    if identifier not in old_identifiers:
        entry = fg.add_entry(order='prepend')
        entry.title(entry_data['title'])
        entry.link(href=entry_data['link'], rel='alternate')
        entry.description(entry_data['description'])
        entry.published(entry_data['published'])

# Then, add all old entries
for entry_data in old_feed_entries:
    entry = fg.add_entry(order='append')
    entry.title(entry_data['title'])
    entry.link(href=entry_data['link'], rel='alternate')
    entry.description(entry_data['description'])
    entry.published(entry_data['published'])

# Generate RSS feed
rssfeed = fg.rss_str(pretty=True)

# Write the RSS feed to a file
with open('npr_corrections_rss.xml', 'wb') as f:
    f.write(rssfeed)

print("RSS feed generated and saved as 'npr_corrections_rss.xml'")
