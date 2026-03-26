import urllib.request
import json
import re

print("Downloading positive words...")
pos_url = "https://raw.githubusercontent.com/jeffreybreen/twitter-sentiment-analysis-tutorial-201107/master/data/opinion-lexicon-English/positive-words.txt"
req = urllib.request.Request(pos_url, headers={'User-Agent': 'Mozilla/5.0'})
pos_data = urllib.request.urlopen(req).read().decode('latin-1')

print("Downloading negative words...")
neg_url = "https://raw.githubusercontent.com/jeffreybreen/twitter-sentiment-analysis-tutorial-201107/master/data/opinion-lexicon-English/negative-words.txt"
req = urllib.request.Request(neg_url, headers={'User-Agent': 'Mozilla/5.0'})
neg_data = urllib.request.urlopen(req).read().decode('latin-1')

def parse_words(text):
    words = []
    for line in text.split('\n'):
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        words.append(line)
    return words

pos_words = parse_words(pos_data)
neg_words = parse_words(neg_data)

# Ensure "die" and variants are in negative
extra_neg = ["die", "suicide", "kill myself", "meaningless", "worthless", "give up on life"]
for word in extra_neg:
    if word not in neg_words:
        neg_words.append(word)

data = {
    "positive": pos_words,
    "negative": neg_words
}

with open("lexicon.json", "w") as f:
    json.dump(data, f)
    
print(f"Saved {len(pos_words)} positive words and {len(neg_words)} negative words to lexicon.json.")
