from pymarc import MARCReader

from utils import save2csv


def find_url(bib):
    phrases = [
        "link.overdrive.com/?website",
    ]

    for field in bib.get_fields("856"):
        if "u" in field:
            for phrase in phrases:
                if phrase in field["u"].lower():
                    url = field["u"].strip()
                    return url


def process(marc_fh, library, sierra_format):
    with open(marc_fh, "rb") as file:
        reader = MARCReader(file)
        no = 0
        for bib in reader:
            # bibNo = bib["907"]["a"][1:]
            # bibFormat = bib["998"]["d"][0]
            oid = bib["037"]["a"]
            no += 1
            url = find_url(bib)

            save2csv(
                f"./reports/{library}/overdrive-{sierra_format}-urls-4scraping.csv",
                [oid, url],
            )


if __name__ == "__main__":
    fh = "./marc/NYPL/missing-eAudio-not-verified.mrc"
    process(fh, "NYPL", "eAudio")
