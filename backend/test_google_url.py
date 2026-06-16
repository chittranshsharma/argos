import re
import requests
html = requests.get('https://news.google.com/rss/articles/CBMifEFVX3lxTE9UcWNHT21RRk15dzlSTTRBOGlOdmE2RHVFUndyS3lfcXpJV1lQQ2ZoTXF5VFlSZk9QLUJxNDJTQUM0c2RDLS1BQ3B6WXdiNUp1aDJEdXRGX25jQi1zdDVvVFprNG1iWWNLNGJpUzZuSFF5a3liUkZOSEt2dWY?oc=5').text
match = re.search(r'<a[^>]*href=\"([^\"]+)\"[^>]*>', html)
print('Found:', match.group(1) if match else 'None')
