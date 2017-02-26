from values import parse_values, dump_values
from series import Series


class Currency(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, c):
        return self.name == c.name


class Rate(object):
    def __init__(self, c1, c2, values):
        self.c1 = c1
        self.c2 = c2
        self.values = values
        self.series = Series(values, "linear", "last")

    def convert(self, date, c, value):
        rate = self.series.calculate(date)
        if self.c1 == c:
            #print "{} {} = {} {} ({})".format(value, self.c1, value*rate, self.c2, rate)
            return value * rate
        elif self.c2 == c:
            #print "{} {} = {} {} ({})".format(value, self.c2, value/rate, self.c1, rate)
            return value / rate
        else:
            raise ValueError("currency mismatch")

    def __eq__(self, pair):
        return set([self.c1, self.c2]) == set(pair)

    def _div(self, r):
        return [tuple((stamp[0], stamp[1] / r.series.calculate(stamp[0]))
            for stamp in interval)
                for interval in self.values]

    def product(self, r):
        """
        self.c1   r.c1
        ------  ; ----
        self.c2   r.c2

        r.c2      self.c1   r.c2
        ------- = ------- * ----
        self.c2   self.c2   r.c1

        self.c1   self.c1  r.c2
        ------- = ------ * ----
        r.c1      self.c2  r.c1
        """
        if self.c1 == r.c1:
            if self.c2 == r.c2:
                return None
            return Rate(r.c2, self.c2, self._div(r))
        elif self.c2 == r.c2:
            return Rate(self.c1, r.c1, self._div(r))
        else:
            return None

    @staticmethod
    def parse(d):
        if "values" in d:
            d["values"] = parse_values(d["values"])
        return Rate(**d)

    def dump(self):
        return {
                "__type__": "Rate",
                "c1": self.c1,
                "c2": self.c2,
                "values": dump_values(self.values)
                }

    def __str__(self):
        return "{}/{}:{}".format(self.c1, self.c2, "")


class Rates(object):
    def __init__(self):
        self.rates = set()
        self.subset = set()

    def get(self, c1, c2):
        #print "Get", c1, c2
        for r in self.rates:
            if r == (c1, c2):
                return r
            if r == (c2, c1):
                return r
        return None

    def add(self, r):
        if self.get(r.c1, r.c2):
            return
        self.subset.add(r)
        self.rates.add(r)
        self.rates |= set(x.product(r) for x in self.rates if x.product(r) is not None)

    @staticmethod
    def parse(d):
        rates = Rates()
        for r in d.get("rates", []):
            rates.add(r)
        for r in rates.rates:
            print r
        return rates

    def dump(self):
        return {
                "__type__": "Rates",
                "rates": [r.dump() for r in self.subset]
                }
