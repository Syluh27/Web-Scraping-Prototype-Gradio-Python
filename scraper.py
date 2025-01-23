import requests
from bs4 import BeautifulSoup


def scrape_quotes():
    url = "http://quotes.toscrape.com/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        quotes_data = []

        for quote_block in soup.find_all("div", class_="quote"):
            text = quote_block.find("span", class_="text").get_text()
            author = quote_block.find("small", class_="author").get_text()
            tags = [tag.get_text() for tag in quote_block.find_all("a", class_="tag")]
            quotes_data.append({
                "quote": text,
                "author": author,
                "tags": tags
            })

        return quotes_data
    else:
        return None


def get_authors_and_tags():
    quotes = scrape_quotes()
    if not quotes:
        return [], []

    authors = sorted(set(q['author'] for q in quotes))
    tags = sorted(set(tag for q in quotes for tag in q['tags']))
    return authors, tags
