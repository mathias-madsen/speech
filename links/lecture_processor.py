""" This module contains classes for handling individual session pages.

A session is a single lecture that may be recorded and subtitles, like
`https://oyc.yale.edu/english/engl-220/lecture-1`. We parse the HTML of
such session pages and look for links to the sound recordings and to the
corresponding subtitles file.
"""

from typing import Optional
from bs4 import BeautifulSoup

from multithreading import Worker
from constants import YALE_URL


def extract_sound_url(lecture_html: str) -> Optional[str]:
    """ Look up the URL of the sound recording of the lecture. """

    page = BeautifulSoup(lecture_html, "html5lib")
    attrs = {"class": "views-field views-field-field-audio--file"}
    wrapper = page.find("td", attrs=attrs)

    if not wrapper:
        raise Exception("Found no 'Audio' column in %r" % lecture_html)

    link = wrapper.find("a", {"rel": "download"})
    
    return link.attrs["href"] if link is not None else None


def infer_subtitles_url(sound_url: Optional[str]) -> Optional[str]:
    """ Guess the URL of the .vtt file with the subtitles for the lecture. """

    if sound_url is None:
        return None

    url_parts = sound_url.split("/")
    name_parts = url_parts[-1].split(".")
    name = ".".join(name_parts[:-1])

    return "%s/sites/default/files/caption-files/%s.vtt" % (YALE_URL, name)


class LectureProcessor(Worker):

    def process(self, lecture_page_html: str) -> None:
        sound = extract_sound_url(lecture_page_html)
        subs = infer_subtitles_url(sound)
        self.output_queue.put((sound, subs))

