import sys
import datetime
import argparse
from collections import namedtuple

from config import load, dump
from import_config import import_csv


def pprinttable(rows, header=False):
    if len(rows) > 1:
        if header:
            headers = rows[0]
            rows = rows[1:]
        else:
            headers = rows[0]._fields
        lens = []
        for i in range(len(rows[0])):
            lens.append(len(max([x[i] for x in rows] + [headers[i]],key=lambda x:len(unicode(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
            if isinstance(rows[0][i], int):
                formats.append("%%%dd" % lens[i])
            else:
                formats.append("%%-%ds" % lens[i])
            hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        print hpattern % tuple(headers)
        print separator
        _u = lambda t: t.decode('UTF-8', 'replace') if isinstance(t, str) else t
        for line in rows:
            print pattern % tuple(_u(t) for t in line)
    elif len(rows) == 1:
        row = rows[0]
        hwidth = len(max(row._fields,key=lambda x: len(x)))
        for i in range(len(row)):
            print "%*s = %s" % (hwidth,row._fields[i],row[i])


def make_plain(src, dst, prefix=""):
    for k, v in src.iteritems():
        if type(v) == dict:
            make_plain(v, dst, prefix + "/" + k)
        else:
            dst[prefix + "/" + k] = v

def do_make_plain(src):
    #print src
    dst = {}
    make_plain(src, dst)
    return {k.replace("/main/", ""): v for k, v in dst.iteritems()}


def percent(x, y):
    if y != 0:
        return "{:.2%}".format(1.0 * x/y - 1)
    return "?"

def percent_yearly(x, y, days):
    if y != 0:
        return "{:.2%}".format((1.0 * x/y)**(365.0/days) - 1)
    return "?"


def do_forecast(calc, currency, last_date, fc_date):
    print "="*79 + "\n" + currency + "\n" + "="*79
    last = calc.investment.calculate_dict(last_date, currency, calc.rates)
    fc = calc.investment.calculate_dict(fc_date, currency, calc.rates)

    last_plain = do_make_plain(last)
    fc_plain = do_make_plain(fc)

    Row = namedtuple("Row", ["name", "last", "forecast", "change", "yearly"])
    rows = [Row("Investment", str(last_date), str(fc_date), "% change", "% yearly")]
    for k in sorted(fc_plain):
        rows.append(Row(
            k,
            "{:.2f}".format(last_plain[k]),
            "{:.2f}".format(fc_plain[k]),
            percent(fc_plain[k], last_plain[k]),
            percent_yearly(fc_plain[k], last_plain[k], (fc_date-last_date).days)))
    pprinttable(rows, True)

def forecast(calc):
    for currency in ["RUR", "USD"]:
        do_forecast(calc, currency, datetime.date(2016, 07, 17), datetime.date(2017, 01, 06))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Calculator")
    parser.add_argument("--config", help="path to config file")
    parser.add_argument("--csv", help="path to csv file")

    args = parser.parse_args()
    calc = None
    if args.csv:
        calc = import_csv(args.csv, 1)
        if args.config:
            dump(args.config, calc.dump())
            sys.exit(0)
    elif args.config:
        calc = load(args.config)
    else:
        parser.print_usage()
        sys.exit(1)

    forecast(calc)
