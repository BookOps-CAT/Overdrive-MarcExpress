import csv

from utils import save2csv


def prep_report(src_fh, dup_type):
    if dup_type == "overdriveNo":
        mindx = 0
    elif dup_type == "controlNo":
        mindx = 2

    unique_ids = set()

    with open(src_fh) as file:
        reader = csv.reader(file)
        for row in reader:
            unique_ids.add(row[mindx])

        print(f"Found {len(unique_ids)} unique ids in the file.")

        for mid in unique_ids:
            bids = []
            oids = []
            cids = []
            fcodes = []
            with open(src_fh) as file:
                reader = csv.reader(file)
                for row in reader:
                    if mid == row[mindx]:
                        bids.append(row[1])
                        oids.append(row[0])
                        cids.append(row[2])
                        fcodes.append(row[3])
                new_row = []
                new_row.extend(bids)
                new_row.extend(oids)
                new_row.extend(cids)
                new_row.extend(fcodes)
                if new_row:
                    save2csv(f"{src_fh[:-4]}-PREP.csv", new_row)


if __name__ == "__main__":
    overdriveNo_dup_fh = "./reports/BPL/overdriveNo-dups.csv"
    controlNo_dup_fh = "./reports/BPL/controlNo-dups.csv"

    prep_report(overdriveNo_dup_fh, "overdriveNo")
