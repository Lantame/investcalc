from values import parse_values, dump_values
from series import Series


class Inflation(object):
    def __init__(self, currency, values):
        self.currency = currency
        self.values = values
        self.aggregate = self._calc(values)
        self.series = Series(self.aggregate, "exponential", "exponential")

    def calculate(self, now, date, value):
        return value * self.series.calculate(date) / self.series.calculate(now)

    def _calc(self, values):
        aggregate = []
        last = 1.0

        for v1, v2 in values:
            current = last * v2[1] ** (1.0 * (v2[0] - v1[0]).days / 365)
            aggregate.append(((v1[0], last), (v2[0], current)))
            last = current

        return aggregate

    @staticmethod
    def parse(d):
        if "values" in d:
            d["values"] = parse_values(d["values"])
        return Inflation(**d)

    def dump(self):
        return {
               "__type__": "Inflation",
               "currency": self.currency,
               "values": dump_values(self.values)
               }

    def __str__(self):
        return "inflation/{}".format(self.currency)


class Inflations(object):
    def __init__(self):
        self.inflations = {}

    def get(self, c):
        return self.inflations.get(c, None)

    def add(self, inflation):
        self.inflations[i.c] = inflation

    @staticmethod
    def parse(d):
        inflations = Inflations()
        for inf in d.get("inflations", []):
            inflations.add(inf)
        for inf in inflations.inflations:
            print inf
        return inflations

    def dump(self):
        return {
                "__type__": "Inflations",
                "inflations": [inf.dump() for inf in self.inflations]
                }
