import json
import logging
from datetime import datetime
from typing import List, Dict, Union

import requests
from bs4 import BeautifulSoup

skip_urls = [
    "/wiki/Category:Living_people",
    "/wiki/Category:Works_by_topic",
    "/wiki/Category:Albums",
    "/wiki/Category:Visual_arts_by_subject",
    "/wiki/Category:Books",
    "/wiki/Category:Formal_sciences",
    "/wiki/Category:Main_topic_classifications",
]


def get_parents(soup: BeautifulSoup) -> Dict[str, str]:
    links = []
    categories = soup.select_one("div[id='mw-normal-catlinks']")
    if categories:
        for link in categories.find_all("ul"):
            links.extend(link.find_all("a", href=True))
    else:
        return {}
    return {x["href"]: x["title"] for x in links}


def get_children(soup: BeautifulSoup) -> Dict[str, str]:
    links = []
    subcategories = soup.select_one("div[id='mw-subcategories']")
    if subcategories:
        for link in subcategories.find_all("ul"):
            links.extend(link.find_all("a", href=True))

    pages = soup.select_one("div[id='mw-pages']")
    if pages:
        for link in pages.find_all("ul"):
            links.extend(link.find_all("a", href=True))

    return {x["href"]: x["title"] for x in links}


def get_title(content: BeautifulSoup) -> str:
    """Safely search for the title of the page. If title element is empty returns 'empty' string"""
    try:
        title = content.find("title").text.strip()
    except AttributeError:
        title = "empty"
    return title[:-12]  # remove " - Wikipedia"


class Crawler:
    logging.basicConfig(
        filename=f"../../data/external/logs-{datetime.now().date()}.txt", level="DEBUG"
    )

    def __init__(self, max_dept):
        self.global_parsed_urls = []  # protects from duplicating crawled websites
        self.MAX_DEPTH = max_dept

    def crawl(
        self, url: str, depth: int = 1, first_n_links: Union[None, int] = None
    ) -> List[Dict[str, str]]:
        """Crawls selected url recursively in a top->down direction."""
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

        # get page title and description
        title = get_title(content=soup)
        parents = get_parents(soup=soup)

        if f"Category:{title}" in parents.values():
            parents.pop(f"/wiki/Category:{url[30:]}")

        category_page_result = None
        if "/wiki/Category:" in url:
            children = get_children(soup=soup)

            child_key = f"/wiki/{url[39:]}"
            if children.get(child_key):

                new_url = f'{"/".join(url.split("/")[:3])}{child_key}'
                category_page_result = self.crawl(
                    new_url, depth=depth - 1, first_n_links=first_n_links
                )
                children.pop(child_key)

        else:
            children = {}

        # create a final dict with crawled page and wrap it into a list
        result = [
            {
                "url": url,
                "title": title,
                "parents": parents,
                "children": children,
                "date": str(datetime.now()),
            }
        ]
        if category_page_result:
            result[0]["title"] = category_page_result[0]["title"]
            result[0]["page_url"] = category_page_result[0]["url"]
            result[0]["parents"].update(category_page_result[0]["parents"])
            result[0]["children"].update(category_page_result[0]["children"])

        # return when depth is exhausted
        if depth == 0:
            return result

        links = []
        links.extend(list(children.keys()))

        if first_n_links and isinstance(first_n_links, int) and first_n_links >= 0:
            links = links[:first_n_links]

        for id_x, link in enumerate(links):
            if depth == self.MAX_DEPTH:
                print(f"{id_x}/{len(links)}:\t{len(result)}\t{link}")

            if link in skip_urls:
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
        "/wiki/Category:Subfields_of_computer_science",
    ]

    final_taxonomy = []
    depth = 4
    for start_page in start_pages:
        url = f"https://en.wikipedia.org{start_page}"

        crawler = Crawler(max_dept=depth)
        result = crawler.crawl(url=url, depth=depth, first_n_links=50)

        final_taxonomy.extend(result)

        print(len(result), len(final_taxonomy))
        final_taxonomy = list({v["url"]: v for v in final_taxonomy}.values())
        print(len(result), len(final_taxonomy))

    with open("../../data/external/wikipedia_taxonomy.json", "w") as fp:
        json.dump(final_taxonomy, fp, indent=2)
