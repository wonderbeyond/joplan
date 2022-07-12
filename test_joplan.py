import datetime as dt
from unittest import mock

from joplan import do, every, take, Job, Plan


def mock_job_func(name=None):
    job_func = mock.Mock()
    job_func.__name__ = name or 'mock_job_func'
    return job_func


class mock_datetime(object):
    """
    Monkey-patch datetime for predictable results
    """

    def __init__(self, t: dt.datetime, /):
        self.time = t

    def __enter__(self):
        class MockDate(dt.datetime):
            @classmethod
            def today(cls):
                return cls(*self.time.timetuple()[:3])

            @classmethod
            def now(cls):
                return self.time

        self.original_datetime = dt.datetime
        dt.datetime = MockDate

        return MockDate(*self.time.timetuple()[:6])

    def __exit__(self, *args, **kwargs):
        dt.datetime = self.original_datetime


def test_job_construction():
    job_func = mock_job_func()

    for job in (
        do(job_func).every('3s'),
        every('3s').do(job_func)
    ):
        assert isinstance(job, Job)
        assert job.interval == dt.timedelta(seconds=3)
        assert job.func is job_func


def test_plan_construction():
    job_func = mock_job_func()
    plan1 = take(
        every('30s').do(job_func),
        every('1min').do(job_func),
    )
    plan2 = Plan([
        every('30s').do(job_func),
        every('1min').do(job_func),
    ])
    assert isinstance(plan1, Plan)
    assert isinstance(plan2, Plan)
    assert plan1 == plan2


def test_plan():
    job_func1 = mock_job_func(name='job_func1')
    job_func2 = mock_job_func(name='job_func2')

    plan = take(
        every('30s').do(job_func1),
        every('1min').do(job_func2),
    )
    initial_time = dt.datetime(3000, 1, 1, 1, 0, 0)

    with mock_datetime(initial_time):

        plan.run(onetime=True)
        assert job_func1.call_count == 1
        assert job_func2.call_count == 1

        plan.run(onetime=True)
        assert job_func1.call_count == 1
        assert job_func2.call_count == 1

        # 31 seconds later
        with mock_datetime(initial_time + dt.timedelta(seconds=31)):
            plan.run(onetime=True)
            assert job_func1.call_count == 2
            assert job_func2.call_count == 1

        # 1 minute and 1 second later
        with mock_datetime(initial_time + dt.timedelta(seconds=61)):
            plan.run(onetime=True)
            assert job_func1.call_count == 3
            assert job_func2.call_count == 2
