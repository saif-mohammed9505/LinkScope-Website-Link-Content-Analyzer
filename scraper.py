from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

DEFAULT_TIMEOUT = 10
SKIP_HREF_PREFIXES = ("#", "javascript:", "mailto:", "tel:")


class FetchError(Exception):
    """Raised when a page can't be fetched or isn't HTML."""


def _get_soup(url, timeout=DEFAULT_TIMEOUT):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FetchError(str(exc)) from exc

    content_type = response.headers.get("Content-Type", "")
    if content_type and "html" not in content_type.lower():
        raise FetchError(f"That URL returned '{content_type.split(';')[0]}', not HTML.")

    return BeautifulSoup(response.content, "html.parser"), response.url


def _clean_links(raw_hrefs, base_url):
    links = []
    seen = set()
    for href in raw_hrefs:
        if not href:
            continue
        href = href.strip()
        if not href or href.lower().startswith(SKIP_HREF_PREFIXES):
            continue
        absolute = urljoin(base_url, href)
        if absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
    return links


def fetch_website_contents(url, max_chars=2000):
    """
    Return the title and contents of the website at the given url;
    truncate to max_chars (default 2,000) as a sensible limit.
    """
    soup, _ = _get_soup(url)
    title = soup.title.get_text(" ", strip=True) if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input", "noscript"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:max_chars]


def fetch_website_links(url):
    """
    Return the absolute, deduplicated links on the website at the given url
    (javascript:, mailto:, tel: and in-page #anchors are excluded).
    """
    soup, final_url = _get_soup(url)
    raw_hrefs = [link.get("href") for link in soup.find_all("a")]
    return _clean_links(raw_hrefs, final_url)


def fetch_website_data(url, max_chars=2000):
    """
    Fetch the page once and return its title, full body text, a truncated
    preview, and its links — avoiding the double-fetch that fetching
    contents and links separately requires.
    """
    soup, final_url = _get_soup(url)
    title = soup.title.get_text(" ", strip=True) if soup.title else "No title found"

    if soup.body:
        raw_hrefs = [link.get("href") for link in soup.body.find_all("a")]
        for irrelevant in soup.body(["script", "style", "img", "input", "noscript"]):
            irrelevant.decompose()
        full_text = soup.body.get_text(separator="\n", strip=True)
    else:
        raw_hrefs = []
        full_text = ""

    links = _clean_links(raw_hrefs, final_url)
    preview = (title + "\n\n" + full_text)[:max_chars]

    return {
        "url": final_url,
        "title": title,
        "full_text": full_text,
        "preview_text": preview,
        "links": links,
    }
