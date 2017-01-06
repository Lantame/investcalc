import math


class ForecastMethod(object):
    def calculate(self, date):
        return 0.0


class LinearForecast(ForecastMethod):
    def __init__(self, values):
        """
        values: [
            ((date1, value1), (date2, value2))
            ]
        """
        self.last = values[-1][1]
        if self.last[1] != 0.0:
            self.rate = self._calc_rate(values)

    def _calc_rate(self, values):
        total_days = 0
        total_change = 0
        for v1, v2 in values:
            if (v2[0] - v1[0]).days <= 1:
                continue
            total_days += (v2[0]-v1[0]).days
            total_change += 1.0*v2[1]/v1[1]-1
        return total_change / total_days

    def calculate(self, date):
        if self.last[1] == 0.0:
            return 0.0
        return self.last[1] * (1 + self.rate * (date-self.last[0]).days)


class ExponentialForecast(ForecastMethod):
    def __init__(self, values):
        self.last = values[-1][1]
        if self.last[1] != 0.0:
            self.rate = self._calc_rate(values)

    def _calc_rate(self, values):
        total_days = 0
        total_change = 1.0
        for v1, v2 in values:
            if (v2[0] - v1[0]).days <= 1:
                continue
            total_days += (v2[0]-v1[0]).days
            total_change *= 1.0*v2[1]/v1[1]
        return math.pow(total_change, 1.0/total_days)

    def calculate(self, date):
        if self.last[1] == 0.0:
            return 0.0
        return self.last[1] * (self.rate ** (date-self.last[0]).days)


class AbsoluteForecast(ForecastMethod):
    def __init__(self, values):
        self.last = values[-1][1]
        if self.last[1] != 0.0:
            self.rate = self._calc_rate(values)

    def _calc_rate(self, values):
        total_days = 0
        total_change = 1.0
        for v1, v2 in values:
            if (v2[0] - v1[0]).days <= 1:
                continue
            total_days += (v2[0]-v1[0]).days
            total_change += v2[1] - v1[1]
        return total_change / total_days

    def calculate(self, date):
        if self.last[1] == 0.0:
            return 0.0
        return self.last[1] + (self.rate * (date-self.last[0]).days)


class LastForecast(ForecastMethod):
    def __init__(self, values):
        self.last = values[-1][1]

    def calculate(self, date):
        return self.last[1]


def build_forecast_method(name, values):
    if name == "linear":
        return LinearForecast(values)
    if name == "exponential":
        return ExponentialForecast(values)
    if name == "absolute":
        return AbsoluteForecast(values)
    if name == "last":
        return LastForecast(values)

    raise ValueError("unknown forecast method: " + name)


class AverageMethod(object):
    def __init__(self, values):
        self.values = values

    def calculate(self, date):
        return 0.0

    def _find_interval(self, date):
        for v1, v2 in self.values:
            if v1[0] <= date and v2[0] >= date:
                return (v1, v2)
        if date < self.values[0][0][0]:
            return None, None
        raise ValueError("interval not found")


class LinearAverage(AverageMethod):
    def __init__(self, values):
        AverageMethod.__init__(self, values)

    def calculate(self, date):
        v1, v2 = self._find_interval(date)
        if v1 is None and v2 is None:
            return 0.0

        rate = (1.0 * v2[1]/v1[1] - 1) / (v2[0]-v1[0]).days
        return v1[1] * (1.0 + rate * (date - v1[0]).days)


class ExponentialAverage(AverageMethod):
    def __init__(self, values):
        AverageMethod.__init__(self, values)

    def calculate(self, date):
        v1, v2 = self._find_interval(date)
        if v1 is None and v2 is None:
            return 0.0

        rate = (1.0 * v2[1]/v1[1]) ** (1.0 / (v2[0]-v1[0]).days)
        return v1[1] * rate ** (date - v1[0]).days


class AbsoluteAverage(AverageMethod):
    def __init__(self, values):
        AverageMethod.__init__(self, values)

    def calculate(self, date):
        v1, v2 = self._find_interval(date)
        if v1 is None and v2 is None:
            return 0.0

        rate = 1.0 * (v2[1] - v1[1]) / (v2[0]-v1[0]).days
        return v1[1] + (rate * (date - v1[0]).days)


class LastAverage(AverageMethod):
    def __init__(self, values):
        AverageMethod.__init__(self, values)

    def calculate(self, date):
        v1, v2 = self._find_interval(date)
        if v1 is None and v2 is None:
            return 0.0

        return v2[1] if date == v2[0] else v1[1]


def build_average_method(name, values):
    if name == "linear":
        return LinearAverage(values)
    if name == "exponential":
        return ExponentialAverage(values)
    if name == "absolute":
        return AbsoluteAverage(values)
    if name == "last":
        return LastAverage(values)

    raise ValueError("unknown average method: " + name)
