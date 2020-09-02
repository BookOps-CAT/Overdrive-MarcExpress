from pymarc import MARCReader
import sys

from utils import save2csv


def parse_overdiveNos(marc_fh, report_fh, sierra_format):
    with open(marc_fh, "rb") as marc:
        reader = MARCReader(marc)
        no = 0
        for bib in reader:
            no += 1
            try:
                overdriveNo = bib["037"]["a"].strip()
            except:
                print(
                    f"Error on bib number: {no} : {sys.exc_info()[0]}:{sys.exc_info()[1]}"
                )
                overdriveNo = None

            try:
                controlNo = bib["001"].data.strip()
            except:
                controlNo = None

            save2csv(report_fh, [overdriveNo, controlNo, sierra_format])
        print(f"File {marc_fh} contains {no} records")


def parse_sierra_bibs(marc_fh, report_fh):
    with open(marc_fh, "rb") as marc:
        reader = MARCReader(marc)
        no = 0
        for bib in reader:
            no += 1
            bibNo = bib["907"]["a"][1:]
            bibFormat = bib["998"]["d"][0]
            bibStatus = bib["998"]["e"]
            overdriveNo = None
            overdriveNoSrc = None
            try:
                for field in bib.get_fields("037"):
                    if "overdrive" in field.value().lower():
                        if "a" in field and field["a"].strip() != "":
                            overdriveNo = field["a"].strip()
                            overdriveNoSrc = "037"
                        break
            except:
                print(
                    f"Error on bib number: {no} : {sys.exc_info()[0]}:{sys.exc_info()[1]}"
                )

            if not overdriveNo:
                # try parsing from url
                try:
                    for field in bib.get_fields("856"):
                        if "u" in field:
                            if "digitalbooks.brooklynpubliclibrary" in field["u"]:
                                idx = field["u"].lower().index("id=")
                                overdriveNo = field["u"][idx + 3 :].strip()
                                overdriveNoSrc = "url"
                                break
                except:
                    overdriveNo = None

            try:
                controlNo = bib["001"].data.strip()
            except:
                controlNo = None

            try:
                controlNoSrc = bib["003"].data.strip()
            except:
                controlNoSrc = None

            save2csv(
                report_fh,
                [
                    overdriveNo,
                    overdriveNoSrc,
                    bibNo,
                    controlNo,
                    controlNoSrc,
                    bibFormat,
                    bibStatus,
                ],
            )
        print(f"File {marc_fh} contains {no} records")


if __name__ == "__main__":

    marc_fh = "./marc/BPL/bpl-sierra-all.mrc"
    report_fh = "./reports/BPL/sierra-bpl-all.csv"

    parse_sierra_bibs(marc_fh, report_fh)
