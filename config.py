import json
import sys

from rate import Rate, Rates
from investment import Investment, InvestmentGroup
from calculator import Calculator
from inflation import Inflation, Inflations

def hook(d):
    if "__type__" not in d:
        return d

    t = d["__type__"]
    del d["__type__"]
    return getattr(sys.modules[__name__], t).parse(d)

def load(config_path):
    with open(config_path) as fp:
        return json.load(fp, object_hook=hook)

def dump(config_path, d):
    print d
    with open(config_path, "w") as fp:
        return json.dump(d, fp, indent=4, sort_keys=True, ensure_ascii=False)
