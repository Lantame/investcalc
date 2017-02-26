from values import parse_values, dump_values
from series import Series


class BaseInvestment(object):
    def calculate(self, date, currency, rates):
        return 0.0

    def calculate_dict(self, date, currency, rates):
        return {}


class Investment(BaseInvestment):
    def __init__(self, name, values, currency, method_name):
        self.series = Series(values, method_name, method_name)
        self.method_name = method_name
        self.name = name
        self.values = values
        self.currency = currency

    def calculate(self, date, currency, rates):
        if self.currency == currency:
            res = self.series.calculate(date)
            #print u"{}: {} {}".format(self.name, res, currency)
            return res

        rate = rates.get(self.currency, currency)
        if rate is not None:
            res = rate.convert(date, self.currency, self.series.calculate(date))
            #print u"{}: {} {}".format(self.name, res, currency)
            return res

        return ValueError("No exchange rate")

    def calculate_dict(self, date, currency, rates):
        return {self.name: self.calculate(date, currency, rates)}

    @staticmethod
    def parse(d):
        if "values" in d:
            d["values"] = parse_values(d["values"])
        return Investment(**d)

    def dump(self):
        return {
                "__type__": "Investment",
                "name": self.name,
                "currency": self.currency,
                "method_name": self.method_name,
                "values": dump_values(self.values)
                }


class InvestmentGroup(BaseInvestment):
    def __init__(self, name, investments):
        self.name = name
        self.investments = investments

    def calculate(self, date, currency, rates):
        return sum(inv.calculate(date, currency, rates) for inv in self.investments)

    def calculate_dict(self, date, currency, rates):
        d = {}
        for inv in self.investments:
            d.update(inv.calculate_dict(date, currency, rates))
        d["total"] = self.calculate(date, currency, rates)
        return {self.name : d}

    @staticmethod
    def parse(d):
        return InvestmentGroup(**d)

    def dump(self):
        return {
                "__type__": "InvestmentGroup",
                "name": self.name,
                "investments": [inv.dump() for inv in self.investments]
                }

