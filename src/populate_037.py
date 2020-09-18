# populates record that miss overdrive # in 037$a if there is overdrive # in one of the URLs

import re

from pymarc import MARCReader, Field

from utils import save2marc


pattern = re.compile(".*(.{8}-.{4}-.{4}-.{4}-.{12}).*")


def has_overdriveNo(bib):
    found = False
    for field in bib.get_fields("037"):
        if "a" in field:
            if pattern.match(field["a"]):
                found = True
    return found


def find_overdriveNo(bib):
    for field in bib.get_fields("856"):
        if "u" in field:
            match = pattern.match(field["u"])
            if match:
                oid = match.group(1)
                return oid.upper()


def process(marc_in, marc_out):
    with open(marc_in, "rb") as file:
        n = 0
        missing_oid = 0
        added_oid = 0
        unable_oid = 0
        reader = MARCReader(file)
        for bib in reader:
            n += 1
            if not has_overdriveNo(bib):
                missing_oid += 1
                oid = find_overdriveNo(bib)
                if oid is not None:
                    added_oid += 1
                    bid = bib["907"]["a"]
                    print(f"processing record no {n}: {bid}, {oid}")
                    bib.remove_fields("037", "994", "948")  # remove MARS
                    t037 = Field(
                        tag="037",
                        indicators=[" ", " "],
                        subfields=[
                            "a",
                            oid,
                            "b",
                            "OverDrive, Inc.",
                            "n",
                            "http://www.overdrive.com",
                        ],
                    )
                    bib.add_ordered_field(t037)
                    t947 = Field(
                        tag="947",
                        indicators=[" ", " "],
                        subfields=["a", "tak/overdrive # added"],
                    )
                    bib.add_ordered_field(t947)
                    # save2marc(marc_out, bib)
                else:
                    save2marc("./marc/BPL/bpl-overdrive-unable-to-add-037.mrc", bib)
                    unable_oid += 1

        print(f"Populated {n} records")
        print(f"Found {missing_oid} records without oid in 037 tag.")
        print(f"Added {added_oid} oids to records.")
        print(f"Unable to add oid to {unable_oid} records")


if __name__ == "__main__":
    process(
        "./marc/BPL/bpl-sierra-all-200917-utf8.mrc",
        "./marc/BPL/bpl-overdrive-037-populated.mrc",
    )
