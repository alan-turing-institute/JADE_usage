import jade_usage.data as data
from pandas import Timedelta
import pytest


@pytest.mark.parametrize(
    'string,days,hours,minutes,seconds',
    [
        ('3-00:00:17', 3, 0, 0, 17),
        ('11:31:17', 0, 11, 31, 17),
        ('1-15:09:20', 1, 15, 9, 20)
    ]
)
def test_elapsed(string, days, hours, minutes, seconds):
    assert data._elapsed(string) == Timedelta(days=days, hours=hours,
                                              minutes=minutes,
                                              seconds=seconds)
