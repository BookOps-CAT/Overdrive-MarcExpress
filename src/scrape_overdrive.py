# Overdrive web scraper scripts
from collections import namedtuple
import csv
import re
import time


import requests
from requests.exceptions import RequestException, Timeout
from bs4 import BeautifulSoup

from utils import save2csv


TIME_OUT = 20  # seconds
TIMEOUT_MAX_OCCURANCE = 10
timeout_count = 0


# regex patterns for significant pieces of info
P = re.compile(r".*window.OverDrive.mediaItems = (\{.*\}\});.*", re.DOTALL)
P_AVAILABLE = re.compile(r'.*"isAvailable":(true|false),".*', re.DOTALL)
P_OWNED = re.compile(r'.*"isOwned":(true|false),".*', re.DOTALL)
P_AVAILABLE_COPIES = re.compile(r'.*"availableCopies":(\d{1,}),".*', re.DOTALL)
P_OWNED_COPIES = re.compile(r'.*"ownedCopies":(\d{1,}),".*', re.DOTALL)

# ebook status data construct
EbookStatus = namedtuple(
    "EbookStatus",
    ["available", "owned", "copies_available", "copies_owned", "for_removal"],
)
EbookStatus.__new__.__defaults__ = (None, None, None, None, None)


def get_html(url):
    """
    retrieves html code from given url
    args:
        url: str
    returns:
        html: bytes
    """

    global timeout_count
    time.sleep(1.0)
    headers = {"user-agent": "tomaszkalata@bookops.org"}
    try:
        response = requests.get(url, headers=headers, timeout=TIME_OUT)
        print("requested page: {} == {}".format(response.url, response.status_code))
        if response.status_code == requests.codes.ok:
            return response.content
    except Timeout:
        # better stop all scraping
        timeout_count += 1
        if timeout_count > TIMEOUT_MAX_OCCURANCE:
            raise Timeout
    except RequestException:
        pass


def determine_for_removal(ebook_status):
    """

    """
    if ebook_status.copies_owned:
        try:
            copies = int(ebook_status.copies_owned)
            if not copies:
                return True
            else:
                return False
        except ValueError:
            return True
        except TypeError:
            return True
    else:
        return True


def update_status(metadata, ebook_status):
    """
    finds significant data in html.head.script
    args:
        html_head_script: str
        ebook_status: namedtuple

    returns:
        updated ebook_status
    """

    # title availability
    match_availability = P_AVAILABLE.match(metadata)
    if match_availability:
        available = match_availability.group(1)
        if available == "true":
            available = True
        elif available == "false":
            available = False
        else:
            available = None
        ebook_status = ebook_status._replace(available=available)

    # title owned
    match_owned = P_OWNED.match(metadata)
    if match_owned:
        owned = match_owned.group(1)
        if owned == "true":
            owned = True
        elif owned == "false":
            owned = False
        else:
            owned = None
        ebook_status = ebook_status._replace(owned=owned)

    # copies available
    match_copies_available = P_AVAILABLE_COPIES.match(metadata)
    if match_copies_available:
        ebook_status = ebook_status._replace(
            copies_available=match_copies_available.group(1)
        )

    # copies owned
    match_copies_owned = P_OWNED_COPIES.match(metadata)
    if match_copies_owned:
        ebook_status = ebook_status._replace(copies_owned=match_copies_owned.group(1))

    for_removal = determine_for_removal(ebook_status)
    ebook_status = ebook_status._replace(for_removal=for_removal)

    return ebook_status


def get_ebook_status(bid, html):
    """
    parses HTML, finds significant portion of metadata in document head, and
    interprets important bits, such as availability of ebook, ownership,
    available copies, and own copies by the library

    args:
        html: response.content
    returns:
        (available, owned, copies_available, copies_owned): namedtuple
    """

    ebook_status = EbookStatus()

    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    for s in scripts:
        m = P.match(str(s))
        if m:
            metadata = m.group(1)
            found = True
            break
    if found:
        ebook_status = update_status(metadata, ebook_status)
    else:
        with open("./temp/missing/{}.html".format(bid), "w") as file:
            file.write(str(html))
    return ebook_status


def construct_url(oid, lib):
    if lib == "BPL":
        return f"https://brooklyn.overdrive.com/media/{oid}"


def scrape(src_fh, lib):
    report = f"./reports/{lib}/overdrive-scraped.csv"
    fh_out_failure = f"./reports/{lib}/overdrive-scraped-failed.csv"
    fh_out_undecoded = f"./reports/{lib}/overdrive-scraped-undecoded.csv"

    with open(src_fh, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            oid = row[0]
            bid = row[1]
            url = construct_url(oid, lib)

            doc = get_html(url)
            if doc:
                # print(doc)
                status = get_ebook_status(bid, doc)

                if status != (None, None, None, None, None):
                    row.extend(status)
                    save2csv(report, row)
                else:
                    save2csv(fh_out_undecoded, row)
            else:

                save2csv(fh_out_failure, row)


if __name__ == "__main__":
    src = "./reports/BPL/expired-before-verification-idsonly.csv"
    # src = "./reports/BPL/testdata4scraping.csv"
    scrape(src, "BPL")
