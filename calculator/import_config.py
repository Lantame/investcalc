import csv
import os.path
import subprocess

from investment import Investment, InvestmentGroup
from values import parse_values
from calculator import Calculator
from rate import Rate, Rates
from inflation import Inflation, Inflations

currencies = ["RUR", "USD", "EUR"]
tmpdir = "/tmp"


def import_values(r, row):
    values = []
    last = None
    # parse investment
    for k in r.fieldnames:
        if k == "":
            continue
        current = (k, float(row[k] if row[k] != "" else 0))
        if last is not None:
            values.append((last, current))
            if last[1] == 0.0:
                last = None
                continue
        if current[1] == 0.0:
            last = None
            continue
        last = current
    return parse_values(values)


def import_csv(filename, params):
    with open(filename) as csvfile:
        for i in xrange(int(params.get("skip", 0))):
            csvfile.readline()
        r = csv.DictReader(csvfile, delimiter=",")
        rates = Rates()
        inflations = Inflations()
        main_group = InvestmentGroup("main", [])
        cur_group = None
        last_group = None
        for row in r:
            print row
            if not row[""]:
                cur_group = last_group = main_group
                continue

            parts = row[""].split("/")
            if len(parts) == 2 and parts[0] in currencies and parts[1] in currencies:
                # rates
                rate = Rate(parts[0], parts[1], import_values(r, row))
                rates.add(rate)
                print "<- {} / {}".format(parts[0], parts[1])
                continue

            if len(parts) == 2 and parts[0].lower() == "inflation":
                # inflations
                inflation = Inflation(parts[1], import_values(r, row))
                inflations.add(inflation)
                print "<- inflation / {}".format(parts[1])
                continue

            if row[""] in currencies:
                last_group = InvestmentGroup(row[""], [])
                cur_group = last_group
                main_group.investments.append(last_group)
                print "<- {}".format(last_group.name)
                continue
            if set(row.values()) == set((row[""], "")):
                last_group = InvestmentGroup(row[""], [])
                cur_group.investments.append(last_group)
                print "<- {} <- {}".format(cur_group.name, last_group.name)
                continue

            if cur_group == last_group and last_group == main_group:
                # Statistics in the end
                continue

            inv = None
            parts = row[""].split("#")
            if len(parts) == 2:
                inv = Investment(parts[0], import_values(r, row), cur_group.name, parts[1])
            else:
                inv = Investment(row[""], import_values(r, row), cur_group.name, "linear")
            last_group.investments.append(inv)
            print "<- {} <- {} <- {}".format(cur_group.name, last_group.name, inv.name)

        return Calculator(main_group, rates, inflations)


def import_libreoffice(filename, params):
    retcode = subprocess.call([
        "libreoffice",
        "--headless",
        "--convert-to",
        "csv:Text - txt - csv (StarCalc):44,34,0,1,1",
        "--outdir",
        tmpdir,
        filename
    ])
    if retcode:
        raise ValueError("failed to convert to CSV: {}".format(filename))

    bn = os.path.basename(filename)
    root, ext = os.path.splitext(bn)
    csvfile = os.path.join(tmpdir, root + ".csv")
    return import_csv(csvfile, params)


def import_file(filename, params):
    if not os.path.exists(filename):
        raise ValueError("path does not exist: {}".format(filename))

    _, ext = os.path.splitext(filename)
    return ext_to_func.get(ext.lower(), import_libreoffice)(filename, params)

ext_to_func = {
        ".csv": import_csv
        }
