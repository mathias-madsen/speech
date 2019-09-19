""" This module contains a function that collects courses descriptions.

The list of course descriptions is compiled on the basis of the table on
`https://oyc.yale.edu/courses`. We parse the HTML of that page and convert
the table rows into `OrderedDict`s. These `OrderedDict`s contain, among
other things, links to the course websites.
"""

import requests  # requests[security] is a requirement!

from collections import OrderedDict
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from constants import YALE_URL


def get_list_of_course_attributes() -> List[OrderedDict]:
    """ Collect a list of course descriptions from the overview page. """

    url = urljoin(YALE_URL, "courses")
    request = requests.get(url)
    page = BeautifulSoup(request.text, "html5lib")
    table, = page.find_all("table", attrs={"class": "views-table cols-5"})
    rows = table.find_all("tr")
    headers = [th.text.strip() for th in rows.pop(0).find_all("th")]

    # find the attributes declared in the table:
    elm_dicts = []
    str_dicts = []
    for row in rows:
        elms = row.find_all("td")
        elm_dicts.append(OrderedDict(zip(headers, elms)))
        strs = [td.text.strip() for td in elms]
        str_dicts.append(OrderedDict(zip(headers, strs)))

    # find and append the course URL too:
    for elm_dict, str_dict in zip(elm_dicts, str_dicts):
        extension = elm_dict["Course title"].find("a").attrs["href"]
        str_dict["course_url"] = urljoin(YALE_URL, extension)
        str_dict["course_id"] = extension.split("/")[-1]

    return str_dicts
