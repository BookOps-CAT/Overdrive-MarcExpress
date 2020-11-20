import csv
from pymarc import MARCReader
from utils import save2csv


def overdrive2list(fh):
    olist = []
    with open(fh, "r") as file:
        reader = csv.reader(file)
        reader.__next__()
        for row in reader:
            olist.append(row[0])
    print(f"Found {len(olist)} records.")
    return olist


def save2marc(marc_out, bib):
    with open(marc_out, "ab") as file:
        file.write(bib.as_marc())


def find_in_marc(marc_src, marc_remove, marc_load, oids):
    with open(marc_src, "rb") as marc_in:
        reader = MARCReader(marc_in)
        matches_found = 0
        matches_not_found = 0
        for bib in reader:
            boid = bib["037"]["a"].strip()
            if boid in oids:
                matches_found += 1
                save2marc(marc_remove, bib)
            else:
                matches_not_found += 1
                save2marc(marc_load, bib)
        print(f"Removed {matches_found} records from the file.")
        print(f"Found {matches_not_found} records that can be imported.")


if __name__ == "__main__":
    src_fh = "./reports/NYPL/overdrive-scraped-failed-eVideo.csv"
    marc_src = "./marc/NYPL/missing-eVideo-not-verified.mrc"
    marc_remove = "./marc/NYPL/missing-eVideo-not-found.mrc"
    marc_load = "./marc/NYPL/missing-eVideo-verified.mrc"

    oids = overdrive2list(src_fh)

    find_in_marc(marc_src, marc_remove, marc_load, oids)
