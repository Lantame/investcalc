class Calculator(object):
    def __init__(self, investment, rates):
        self.investment = investment
        self.rates = rates

    @staticmethod
    def parse(d):
        return Calculator(**d)

    def dump(self):
        return {
                "__type__": "Calculator",
                "investment": self.investment.dump(),
                "rates": self.rates.dump()
                }
