import json
import logging
from datetime import datetime
from typing import List, Dict, Union

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

blacklist = [
    "/wiki/Category:Living_people",
    "/wiki/Category:Works_by_topic",
    "/wiki/Category:Albums",
    "/wiki/Category:Visual_arts_by_subject",
    "/wiki/Category:Books",
    "/wiki/Category:Formal_sciences",
    "/wiki/Category:Main_topic_classifications",
]


def get_parents(soup: BeautifulSoup) -> Dict[str, str]:
    links = soup.select_one("div[id='mw-normal-catlinks']")
    if links:
        links = links.find("ul").find_all("a", href=True)
    else:
        return {}
    return {x["href"]: x["title"] for x in links}


def get_children(soup: BeautifulSoup) -> Dict[str, str]:
    links = []
    subcategories = soup.select_one("div[id='mw-subcategories']")
    if subcategories:
        links.extend(subcategories.find("ul").find_all("a", href=True))

    pages = soup.select_one("div[id='mw-pages']")
    if pages:
        links.extend(pages.find("ul").find_all("a", href=True))

    return {x["href"]: x["title"] for x in links}


def get_title(content: BeautifulSoup) -> str:
    """Safely search for the title of the page. If title element is empty returns 'empty' string"""
    try:
        title = content.find("title").text.strip()
    except AttributeError:
        title = "empty"
    return title


class Crawler:
    logging.basicConfig(
        filename=f"../data/logs-{datetime.now().date()}.txt", level="DEBUG"
    )

    def __init__(self, MAX_DEPTH):
        self.global_parsed_urls = []  # protects from duplicating crawled websites
        self.MAX_DEPTH = MAX_DEPTH

    def crawl(
        self, url: str, depth: int = 1, first_n_links: Union[None, int] = None
    ) -> List[Dict[str, str]]:

        logging.debug("crawling: %s at depth %d" % (url, depth))
        self.global_parsed_urls.append(url)
        logging.debug("%d unique urls parsed so far" % len(self.global_parsed_urls))

        # try to perform HTTP GET request
        try:
            response = requests.get(url, headers={"user-agent": "SimpleFind"})
        except requests.exceptions.SSLError:
            print("SSLError: URL %s doesn't work" % url)
            logging.error("SSLError: URL %s doesn't work" % url)
            return list()
        except requests.exceptions.ConnectionError:
            print("ConnectionError: URL %s doesn't work" % url)
            logging.error("ConnectionError: URL %s doesn't work" % url)
            return list()

        # parse response page content
        soup = BeautifulSoup(response.text, "lxml")

        # # get page title and description
        title = get_title(content=soup)
        parents = get_parents(soup=soup)

        if "/wiki/Category:" in url:
            children = get_children(soup=soup)
        else:
            children = {}

        # create a final dict with crawled page and wrap it into a list
        result = [
            {
                "@context": "https://en.wikipedia.org/",
                "@id": url,
                "url": url,
                "title": title,
                "parents": parents,
                "children": children,
                "date": str(datetime.now()),
            }
        ]

        # return when depth is exhausted
        if depth == 0:
            return result

        links = list(parents.keys())
        links.extend(list(children.keys()))

        if first_n_links and isinstance(first_n_links, int) and first_n_links >= 0:
            links = links[:first_n_links]

        for link in tqdm(links):
            if link in blacklist:
                continue

            if link.startswith("https://") and link not in self.global_parsed_urls:
                new_url = link
            elif link.startswith("/"):
                new_url = f'{"/".join(url.split("/")[:3])}{link}'
                if new_url in self.global_parsed_urls:
                    continue
            else:
                continue

            try:
                logging.debug("following url: %s" % new_url)
                child_result = self.crawl(
                    new_url, depth=depth - 1, first_n_links=first_n_links
                )
                result.extend(child_result)
            except KeyError:
                pass

        return result


if __name__ == "__main__":
    start_pages = [
        "/wiki/Category:Data_mining",
        "/wiki/Category:Mathematics",
        "/wiki/Category:Cryptography",
        "/wiki/DBSCAN",
        "/wiki/Generative_adversarial_network",
    ]

    final_results = []
    depth = 5
    for start_page in start_pages:
        url = f"https://en.wikipedia.org{start_page}"

        crawler = Crawler(MAX_DEPTH=depth)
        result = crawler.crawl(url=url, depth=depth)

        final_results.extend(result)

        print(len(result), len(final_results))
        final_results = list({v["url"]: v for v in final_results}.values())
        print(len(result), len(final_results))

    with open("../result.json", "w") as fp:
        json.dump(final_results, fp, indent=2)
