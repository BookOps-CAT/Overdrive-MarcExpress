import csv


def count_isbns(fh):
    with open(fh, "r") as file:
        reader = csv.reader(file)
        present = 0
        missing = 0
        for row in reader:
            if row == []:
                missing += 1
            else:
                present += 1

        print(f"Present: {present}, missing {missing}")


if __name__ == "__main__":
    fh = "./marc/BPL/ebook-isbns.txt"
    count_isbns(fh)
