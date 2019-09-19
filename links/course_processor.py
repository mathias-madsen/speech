""" This module contains classes for handling course pages.

An example of a course page is `https://oyc.yale.edu/english/engl-220`.
Course pages contain a table of sessions, with links to the individual
session pages. We collect the list of such links in a multi-threaded
processes and open these links in further subprocesses.
"""

from queue import Queue
from typing import List
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from multithreading import download
from multithreading import Worker
from constants import YALE_URL
from lecture_processor import LectureProcessor


def extract_lecture_urls(course_page_html: str) -> List[str]:
    """ Scrape the links to the lectures off the 'Sessions' table. """

    # Find the table of sessions:
    page = BeautifulSoup(course_page_html, "html5lib")
    wrapper = page.find("div", attrs={"id": "quicktabs-tabpage-course-2"})
    table = wrapper.find("table", attrs={"class": "views-table cols-0"})
    # table = page.find("table", attrs={"class": "views-table cols-0"})
    rows = table.find_all("tr")

    # Extract the URLs as strings from the table cells:
    lecture_urls = []
    for row in rows:
        number, name = row.find_all("td")
        extension = name.find("a").attrs["href"]
        lecture_url = urljoin(YALE_URL, extension)
        lecture_urls.append(lecture_url)
    
    return lecture_urls


class CourseProcessor(Worker):

    num_subthreads = 5

    def process(self, course_page_html: str) -> None:
        
        lecture_urls = extract_lecture_urls(course_page_html)
        lecture_pages = download(lecture_urls)

        input_queue = Queue()  # type: ignore
        for lpg in lecture_pages:
            input_queue.put(lpg)

        # All the sub-workers write to the same shared output queue,
        # which is also why we can't use the usual `multiprocess`:
        threads = [LectureProcessor(input_queue, self.output_queue)
                   for _ in range(self.num_subthreads)]

        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
