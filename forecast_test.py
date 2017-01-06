from datetime import date
from forecast import *


data = [
    ((date(2000, 1, 1), 100), (date(2000, 1, 3), 400))
    ]

avg_date = date(2000, 1, 2)
fc_date = date(2000, 1, 4)


class TestAverage(object):
    def test_linear(self):
        f = LinearAverage(data)
        assert f.calculate(avg_date) == 250.0

    def test_exponential(self):
        f = ExponentialAverage(data)
        assert f.calculate(avg_date) == 200.0


class TestForecast(object):
    def test_linear(self):
        f = LinearForecast(data)
        assert f.calculate(fc_date) == 1000

    def test_exponential(self):
        f = ExponentialForecast(data)
        assert f.calculate(fc_date) == 800
