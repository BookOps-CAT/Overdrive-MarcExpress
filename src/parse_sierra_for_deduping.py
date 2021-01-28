# use for deduping dataset

from pymarc import MARCReader
import sys
import re

from utils import save2csv


def find_url(bib):
    phrases = [
        "link.overdrive.com/?website",
        "http://digitalbooks.brooklynpubliclibrary.org/ContentDetails",
    ]
    urls = []
    for field in bib.get_fields("856"):
        if "u" in field:
            for phrase in phrases:
                if phrase in field["u"].lower():
                    url = field["u"].strip()
                    urls.append(url)
    return urls


def parse_sierra_file(marc_in, report):
    with open(marc_fh, "rb") as marc:
        pattern = re.compile(".*-.*-.*-.*-.*")
        reader = MARCReader(marc)
        no = 0
        for bib in reader:
            no += 1
            oid_found = False
            bibNo = bib["907"]["a"][1:]
            bibFormat = bib["998"]["d"][0]
            bibStatus = bib["998"]["e"]
            overdriveNo = None

            try:
                callNumber = bib["099"].value()
            except:
                callNumber = None

            try:
                controlNo = bib["001"].data.strip()
            except:
                controlNo = None

            # record urls
            urls = find_url(bib)
            urls = "^".join(urls)

            # records may have multiple overdrive #
            try:
                for field in bib.get_fields("037"):
                    for subfield in field.get_subfields("a"):
                        if re.match(pattern, subfield):
                            oid_found = True
                            overdriveNo = subfield.strip()
                            save2csv(
                                report,
                                [
                                    overdriveNo,
                                    bibNo,
                                    controlNo,
                                    bibFormat,
                                    bibStatus,
                                    urls,
                                ],
                            )
            except:
                print(
                    f"Error on bib number: {no} : {sys.exc_info()[0]}:{sys.exc_info()[1]}"
                )

            if not oid_found:
                save2csv(
                    report,
                    [overdriveNo, bibNo, controlNo, bibFormat, bibStatus, urls],
                )


if __name__ == "__main__":
    marc_fh = "./marc/BPL/Overdrive-ALL-210128-utf8.mrc"
    report_fh = "./reports/BPL/bpl-dedup-data.csv"

    parse_sierra_file(marc_fh, report_fh)
