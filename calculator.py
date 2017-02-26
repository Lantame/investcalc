class Calculator(object):
    def __init__(self, investment, rates, inflations):
        self.investment = investment
        self.rates = rates
        self.inflations = inflations

    @staticmethod
    def parse(d):
        return Calculator(**d)

    def dump(self):
        return {
                "__type__": "Calculator",
                "investment": self.investment.dump(),
                "rates": self.rates.dump(),
                "inflations": self.inflations.dump()
                }
