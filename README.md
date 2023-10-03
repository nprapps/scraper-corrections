# corrections-scraper
 
This uses Beautiful Soup to scrape the https://www.npr.org/corrections/ page and convert it to an RSS feed that is used to run the NPR #corrections slack channel. 

A Github action runs the script and checks for changes every hour. If it detects changes, it updates npr_corrections_rss.xml.

Once the publishing/deploy action runs, the feed can be accessed at https://blog.apps.npr.org/scraper-corrections/npr_corrections_rss.xml. Changes will appear a minute or two after the action runs.
