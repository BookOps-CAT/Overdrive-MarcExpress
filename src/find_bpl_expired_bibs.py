"""
Scripts to query BPL Solr to find expired/removed Overdrive records
"""

import json
import os
import time
from bookops_bpl_solr import SolrSession


from utils import save2csv


def get_creds(fh):
    with open(fh, "rb") as jsonfile:
        creds = json.load(jsonfile)
        return creds


def find_total_hits(response):
    return response.json()["response"]["numFound"]


def calc_number_of_requests_needed(rows, total_hits):
    left_over = total_hits % rows
    req_loops = int(total_hits / rows)
    if left_over:
        req_loops += 1

    return req_loops


def extract_data(response, out):
    data = response.json()
    docs = data["response"]["docs"]
    for d in docs:
        row = [
            f"b{d['id']}a",
            d["material_type"],
            d["econtrolnumber"],
            d["eurl"],
            d["digital_avail_type"],
            d["digital_copies_owned"],
        ]
        save2csv(out, row)


def make_page_request(session, start):
    response = session.find_expired_econtent(rows=50, result_page=start)
    print(f"Result page #: {start} = {response.status_code}, url={response.url}")
    return response


def find_expired_bibs(creds):
    out = "./reports/BPL/expired_solr.csv"
    save2csv(
        out,
        ["bib #", "format", "reserve #", "url", "availability type", "owned copies"],
    )

    with SolrSession(
        authorization=creds["client_key"], endpoint=creds["endpoint"]
    ) as session:
        response = session.find_expired_econtent(rows=50)
        print(f"Initial request response = {response.status_code}")
        result_page = 0

        total_hits = find_total_hits(response)
        print(f"Total hits: {total_hits}")

        req_loops = calc_number_of_requests_needed(50, total_hits)
        for l in range(req_loops):
            response = make_page_request(session, start=50 * l)
            extract_data(response, out)
            time.sleep(1)


def find_bib(creds):
    with SolrSession(
        authorization=creds["client_key"], endpoint=creds["endpoint"]
    ) as session:
        response = session.search_bibNo(
            keyword="b112411083", default_response_fields=False
        )
        print(response.json())


if __name__ == "__main__":
    cred_fh = os.path.join(os.environ["USERPROFILE"], ".bpl-solr\\bpl-solr-prod.json")
    creds = get_creds(cred_fh)
    # find_expired_bibs(creds)
    find_bib(creds)
