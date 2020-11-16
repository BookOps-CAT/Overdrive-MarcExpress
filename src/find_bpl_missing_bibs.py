import csv
from collections import OrderedDict

from pymarc import MARCReader
from utils import save2csv


def overdrive2list(fh, sierra_format):
    olist = []
    with open(fh, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if sierra_format == row[7]:
                olist.append(row[6])
    print(f"Found {len(olist)} records in format {sierra_format}")
    return olist


def save2marc(marc_out, bib):
    with open(marc_out, "ab") as file:
        file.write(bib.as_marc())


def find_in_marc(marc_src, oids, sierra_format):
    marc_out = f"./marc/BPL/missing-{sierra_format}.mrc"
    with open(marc_src, "rb") as marc_in:
        reader = MARCReader(marc_in)
        matches_found = 0
        for bib in reader:
            boid = bib["037"]["a"].strip()
            if boid in oids:
                matches_found += 1
                save2marc(marc_out, bib)
        print(f"Found {matches_found}.")


def extract_ids_from_overdrive_marc(marc_in, oids, sierra_format):
    report = f"./reports/BPL/missing-combined-ids.csv"
    with open(marc_in, "rb") as marc:
        reader = MARCReader(marc)
        for bib in reader:
            isbn_present = False
            oid = bib["037"]["a"].strip()
            if oid in oids:
                try:
                    controlNo = bib["001"].data.lower().strip()
                except:
                    controlNo = None

                for field in bib.get_fields("020"):
                    for subfield in field.get_subfields("a"):
                        isbn = subfield.split(" ")[0].lower().strip()
                        if isbn:
                            isbn_present = True
                            save2csv(report, [isbn, controlNo, oid, sierra_format])
                if not isbn_present and controlNo:
                    save2csv(
                        report,
                        [None, controlNo, oid, sierra_format],
                    )


def extract_ids_from_sierra_marc(marc_in, report):
    with open(marc_in, "rb") as marc:
        reader = MARCReader(marc)
        for bib in reader:
            bibNo = bib["907"]["a"][1:]
            bibFormat = bib["998"]["d"][0]
            bibStatus = bib["998"]["e"]
            try:
                controlNo = bib["001"].data.lower().strip()
            except:
                controlNo = None

            for field in bib.get_fields("020"):
                for subfield in field.get_subfields("a"):
                    isbn = subfield.split(" ")[0].lower().strip()
                    if isbn:
                        save2csv(report, [isbn, controlNo, bibNo, bibFormat, bibStatus])


def map2dict(csv_fh):
    oids = OrderedDict()
    with open(csv_fh, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            oids[row[0]] = row[1]

    return oids


def find_match_in_sierra_file(oisbns, marc_sierra, report_matched, marc_matched):
    with open(marc_sierra, "rb") as marc_in:
        reader = MARCReader(marc_in)
        for bib in reader:
            bisbns = []
            for field in bib.get_fields("020"):
                for subfield in field.get_subfields("a"):
                    bisbns.append(subfield.split(" ")[0].strip())
            for i in bisbns:
                if i in oisbns.keys():
                    # found match!
                    save2marc(marc_matched, bib)
                    save2csv(report_matched, [i])
                    break


if __name__ == "__main__":
    marc_sierra = "./marc/BPL/bpl-sierra-all.mrc"
    report_fh = "./reports/BPL/missing.csv"

    marc_ovideo = "./marc/BPL/od-bpl-all-evideo.mrc"
    marc_oaudio = "./marc/BPL/od-bpl-all-eaudio.mrc"
    marc_obook = "./marc/BPL/od-bpl-all-ebook.mrc"

    report_sierra_ids = "./reports/BPL/sierra-ids.csv"

    # marc_out_evideo = "./marc/BPL/missing-evideo-2.mrc"
    # marc_out_eaudio = "./marc/BPL/missing-eaudio-2.mrc"
    # marc_out_ebook = "./marc/BPL/missing-ebook-2.mrc"

    # missing_ids = overdrive2list(report_fh, "x")
    # extract_ids_from_overdrive_marc(marc_obook, missing_ids, "x")

    # extract_ids_from_sierra_marc(marc_sierra, report_sierra_ids)

    report = "./reports/BPL/missing-verified.csv"
    oids = overdrive2list(report, "x")
    find_in_marc(marc_obook, oids, "book")
