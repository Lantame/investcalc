from datetime import datetime

"""
[
    (
        (date1, value1),
        (date2, value2)
    ),
    ...
]
"""

FORMAT = "%d.%m.%Y"

def parse_values(values):
    return [tuple((datetime.strptime(stamp[0], FORMAT).date(), stamp[1])
        for stamp in interval)
            for interval in values]

def dump_values(values):
    return [tuple((stamp[0].strftime(FORMAT), stamp[1])
            for stamp in interval)
                for interval in values]
