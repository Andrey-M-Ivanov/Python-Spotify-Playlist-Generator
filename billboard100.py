from bs4 import BeautifulSoup
import requests

site = f"https://www.billboard.com/charts/hot-100/"


def get_html_document(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def get_songs_names(date):
    html_document = get_html_document(site+date)
    soup = BeautifulSoup(html_document, "html.parser")

    all_songs = soup.find_all(name="div", class_="o-chart-results-list-row-container")
    titles = [song.h3.get_text().strip() for song in all_songs]

    return titles
