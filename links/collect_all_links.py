""" This script collects links to sound and subtitle files.

Executing this script as a __main__ will cause the download of course
and lecture pages, and the extraction of links to sound files and
subtitles from the lecture pages.
"""

import os
import json

from time import perf_counter

from multithreading import download
from multithreading import multiprocess
from constants import DATA_DIR
from course_list import get_list_of_course_attributes
from course_processor import CourseProcessor


if __name__ == "__main__":

    print("Starting link-collection; this may take a couple of minutes . . . ")
    start = perf_counter()

    courses = get_list_of_course_attributes()
    course_urls = [course["course_url"] for course in courses]
    course_pages = download(course_urls)
    results = multiprocess(course_pages, CourseProcessor, num_threads=5)

    dur = perf_counter() - start
    print("Done: found %s results in %.3f seconds.\n" % (len(results), dur))

    json_path = os.path.join(DATA_DIR, "all_links.json")

    data = dict(sound_urls=[sound for sound, subs in results],
                subtitle_urls=[subs for sound, subs in results])
    
    with open(json_path, "wt") as destination:
        json.dump(data, destination, indent=4)
