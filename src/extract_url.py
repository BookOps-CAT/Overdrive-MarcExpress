from pymarc import MARCReader

from utils import save2csv


def find_url(bib):
    phrases = [
        "link.overdrive.com/?websiteid=89",
        "digitalbooks.brooklynpubliclibrary.org",
        "https://brooklyn.overdrive.com/media/",
    ]

    for field in bib.get_fields("856"):
        if "u" in field:
            for phrase in phrases:
                if phrase in field["u"].lower():
                    url = field["u"].strip()
                    return url


def process(marc_fh, library):
    with open(marc_fh, "rb") as file:
        reader = MARCReader(file)
        no = 0
        for bib in reader:
            bibNo = bib["907"]["a"][1:]
            bibFormat = bib["998"]["d"][0]
            no += 1
            url = find_url(bib)

            save2csv(f"./reports/{library}/overdrive-urls.csv", [bibNo, bibFormat, url])


if __name__ == "__main__":
    fh = "./marc/BPL/Overdrive4deletion.mrc"
    process(fh, "BPL")
