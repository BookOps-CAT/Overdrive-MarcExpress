from pymarc import MARCReader
import sys
import re

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
        pattern = re.compile(".*-.*-.*-.*-.*")
        reader = MARCReader(marc)
        no = 0
        for bib in reader:
            no += 1
            found_oid = False
            bibNo = bib["907"]["a"][1:]
            bibFormat = bib["998"]["d"][0]
            bibStatus = bib["998"]["e"]

            try:
                controlNo = bib["001"].data.strip()
            except:
                controlNo = None

            try:
                controlNoSrc = bib["003"].data.strip()
            except:
                controlNoSrc = None

            try:
                for field in bib.get_fields("037"):
                    for subfield in field.get_subfields("a"):
                        if re.match(pattern, subfield):
                            found_oid = True
                            overdriveNo = field["a"].strip()
                            overdriveNoSrc = "037"
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

            except:
                print(
                    f"Error on bib number: {no} : {sys.exc_info()[0]}:{sys.exc_info()[1]}"
                )

            # try:
            #     for field in bib.get_fields("856"):
            #         for subfield in field.get_subfields("u"):
            #             if (
            #                 "ebooks.nypl.org/ContentDetails" in field["u"]
            #                 or "link.overdrive.com/?website" in field["u"]
            #             ):
            #                 found_oid = True
            #                 idx = field["u"].lower().index("id=")
            #                 overdriveNo = field["u"][idx + 3 :].strip()
            #                 overdriveNoSrc = "url"
            #                 save2csv(
            #                     report_fh,
            #                     [
            #                         overdriveNo,
            #                         overdriveNoSrc,
            #                         bibNo,
            #                         controlNo,
            #                         controlNoSrc,
            #                         bibFormat,
            #                         bibStatus,
            #                     ],
            #                 )
            # except:
            #     print(
            #         f"Error on bib number: {no} : {sys.exc_info()[0]}:{sys.exc_info()[1]}"
            #     )

            # if not found_oid:
            #     save2csv(
            #         report_fh,
            #         [
            #             overdriveNo,
            #             overdriveNoSrc,
            #             bibNo,
            #             controlNo,
            #             controlNoSrc,
            #             bibFormat,
            #             bibStatus,
            #         ],
            #     )

        print(f"File {marc_fh} contains {no} records")


if __name__ == "__main__":

    # marc_fh = "./marc/NYPL/sierra-nyp-all-prepped.mrc"
    # report_fh = "./reports/NYPL/sierra-nyp-all.csv"

    # parse_sierra_bibs(marc_fh, report_fh)

    marc_fh = "./marc/NYPL/orig/od-nyp-all-ebook-utf8.mrc"
    report_fh = "./reports/NYPL/od-nyp-all.csv"
    sierra_format = "z"

    parse_overdiveNos(marc_fh, report_fh, sierra_format)
