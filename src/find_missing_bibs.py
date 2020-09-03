import csv

from pymarc import MARCReader


def overdrive2list(fh, sierra_format):
    olist = []
    with open(fh, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if sierra_format == row[8]:
                olist.append(row[0])
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


if __name__ == "__main__":
    report_fh = "./reports/BPL/missing.csv"
    marc_ovideo = "./marc/BPL/od-bpl-all-evideo.mrc"
    marc_oaudio = "./marc/BPL/od-bpl-all-eaudio.mrc"
    marc_ebook = "./marc/BPL/od-bpl-all-ebook.mrc"

    marc_out_evideo = "./marc/BPL/missing-evideo.mrc"
    marc_out_eaudio = "./marc/BPL/missing-eaudio.mrc"
    marc_out_ebook = "./marc/BPL/missing-ebook.mrc"

    oids = overdrive2list(report_fh, "x")
    find_in_marc(marc_ebook, oids, marc_out_ebook)
