import csv
from collections import OrderedDict

from pymarc import MARCReader
from utils import save2csv


def overdrive2list(fh, sierra_format):
    olist = []
    with open(fh, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if sierra_format == row[5]:
                olist.append(row[1])
    print(f"Found {len(olist)} records in format {sierra_format}")
    return olist


def save2marc(marc_out, bib):
    with open(marc_out, "ab") as file:
        file.write(bib.as_marc())


def find_in_marc(marc_fh, oids, marc_out):
    with open(marc_fh, "rb") as marc_in:
        reader = MARCReader(marc_in)
        matches_found = 0
        for bib in reader:
            boid = bib["037"]["a"].strip()
            if boid in oids:
                matches_found += 1
                save2marc(marc_out, bib)
        print(f"Found {matches_found}.")


def extract_isbns_from_marc(marc_in, sierra_format, marc_out):
    with open(marc_in, "rb") as marc:
        reader = MARCReader(marc)
        hopeless = 0
        for_verification = 0
        for bib in reader:
            oid = bib["037"]["a"].strip()
            isbn = bib.isbn()
            if isbn is not None:
                for_verification += 1
                save2csv(
                    f"./reports/BPL/missing-{sierra_format}-isbns-for-verification.csv",
                    [isbn, oid],
                )
            else:
                hopeless += 1
                save2marc(marc_out, bib)

        print(
            f"Found {for_verification} records for verfication and {hopeless} hopeless."
        )


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
    report_fh = "./reports/BPL/missing_verified-1.csv"

    marc_ovideo = "./marc/BPL/od-bpl-all-evideo.mrc"
    marc_oaudio = "./marc/BPL/od-bpl-all-eaudio.mrc"
    marc_ebook = "./marc/BPL/od-bpl-all-ebook.mrc"

    marc_out_evideo = "./marc/BPL/missing-evideo-2.mrc"
    marc_out_eaudio = "./marc/BPL/missing-eaudio-2.mrc"
    marc_out_ebook = "./marc/BPL/missing-ebook-2.mrc"

    # missing_isbns = "./reports/BPL/missing-isbns-verification.csv"

    # this we probably should simply load but could run a verification in OCLC
    # we may have some duplicates here, maybe author/title search in Solr?
    hopeless_missing_ebook = "./marc/BPL/hopeless_missing_ebook.mrc"
    hopeless_missing_eaudio = "./marc/BPL/hopeless_missing_eaudio.mrc"
    hopeless_missing_evideo = "./marc/BPL/hopeless_missing_evideo.mrc"

    # oids = overdrive2list(report_fh, "x")
    # find_in_marc(marc_ebook, oids, marc_out_ebook)
    extract_isbns_from_marc(marc_out_ebook, "book", hopeless_missing_ebook)

    # use this one to filter out from missing.mrc file
    # report_matched_ebook = "./reports/BPL/matched_ebooks.csv"

    # marc_ebook_matched = "./marc/BPL/sierra_ebooks_matched.mrc"

    # oids = map2dict(missing_isbns)
    # find_match_in_sierra_file(
    #     oids, marc_sierra, report_matched_ebook, marc_ebook_matched
    # )
