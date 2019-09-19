import pycurl
from io import BytesIO

from typing import Any
from typing import List
from typing import Callable

from threading import Thread

from queue import Queue
from queue import Empty

from time import perf_counter


class Worker(Thread):

    def __init__(self, input_queue: Queue, output_queue: Queue) -> None:
        self.input_queue = input_queue
        self.output_queue = output_queue
        Thread.__init__(self)
    
    def process(self, input_element: Any) -> None:
        """ Do something to the input and put the result in the output_quueue. """

        raise NotImplementedError

    def run(self) -> None:
        """ Proces elements from the input queue until empty. """

        while True:
            try:
                input_element = self.input_queue.get_nowait()
                self.process(input_element)
            except Empty:
                return


def single_file_download(url: str, encoding: str = "utf-8") -> str:
    """ Download a single file from the web, single-threaded. """

    recipient = BytesIO()  # the stream we will write into

    # print("Opening %r . . ." % url)
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, recipient)
    curl.perform()
    curl.close()
    # print("Closed %r." % url)

    return recipient.getvalue().decode(encoding)


class Downloader(Worker):

    def process(self, url: str) -> None:
        """ Get the contents of the file at the given url. """

        text = single_file_download(url, encoding="utf-8")
        self.output_queue.put(text)


def get_all_nowait(queue: Queue) -> list:
    """ Pop all elements out of a queue using .get_nowait(). """

    results = []

    while True:
        try:
            result = queue.get_nowait()
            results.append(result)
        except Empty:
            break

    return results



def multiprocess(inputs: list, worker_class: Any, num_threads: int = 40):
    """ Process every input using the given worker class. """

    input_queue = Queue()  # type: ignore
    output_queue = Queue()  # type: ignore

    for input_elm in inputs:
        input_queue.put(input_elm)

    threads = [worker_class(input_queue, output_queue)
               for _ in range(num_threads)]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()

    return get_all_nowait(output_queue)


def download(urls: List[str], num_threads: int = 40) -> List[str]:
    """ Read a file from the internet, and put it in a folder on disk.
    
    This function took inspiration from the following PyCurl example:
    `https://github.com/pycurl/pycurl/blob/master/examples/retriever.py`.
    """

    num_files = len(urls)
    start = perf_counter()

    print("Starting download of %s files . . ." % num_files)

    results = multiprocess(urls, Downloader, num_threads=num_threads)

    dur = perf_counter() - start
    print("Completed download of %s files after %.3f seconds." % (num_files, dur))

    return results
