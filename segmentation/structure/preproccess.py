from bs4 import BeautifulSoup
import re


def strip(html_doc):
    doc = re.sub("[\s]+", " ", html_doc)
    soup = BeautifulSoup(doc)
    # strip head
    body = soup.find("body")
    for s in body.find_all('script'):
        s.decompose()
    for s in body.find_all('noscript'):
        s.decompose()
    for s in body.find_all('link'):
        s.decompose()
    for s in body.find_all('iframe'):
        s.decompose()
    return body


def break_up(page):

    # tags that could be segments
    segment_tags = {"div", "head", "table", "center", "body", "section", "p", "span", "ul"}

    def search(tag):
        if hasattr(tag, 'children'):
            children = {c.name for c in tag.children}
            if len(segment_tags & children) == 0:
                return [tag]
            else:
                ret_list = []
                for c in tag.children:
                    if c.name in segment_tags:
                        ret_list.extend(search(c))
                return ret_list

    return search(page)


def prepare(page):
    stripped = strip(page)
    broken = break_up(stripped)
    return broken


