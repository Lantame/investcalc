from forecast import build_average_method, build_forecast_method


class Series(object):
    def __init__(self, values, average_method, forecast_method):
        self.values = values
        self.average = build_average_method(average_method, values)
        self.forecast = build_forecast_method(forecast_method, values)
        self.last = values[-1][1]

    def calculate(self, date):
        if date > self.last[0]:
            return self.forecast.calculate(date)
        return self.average.calculate(date)

