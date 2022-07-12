from typing import cast, Union, Dict, Optional, Callable, Iterable
import time
import logging
import datetime as dt
import dataclasses as dc

from deltaman import delta_parser

from joplan.utils import import_from_string

logger = logging.getLogger(__name__)

JobIntervalInType = str
JobFuncInType = Union[str, Callable]


def _parse_interval(interval: JobIntervalInType) -> dt.timedelta:
    return delta_parser.parse(interval)


def _parse_func(func: JobFuncInType) -> Callable:
    return import_from_string(func) if isinstance(func, str) else func


@dc.dataclass
class Job:
    interval: Optional[dt.timedelta] = None
    func: Optional[Callable] = None

    def __repr__(self):
        return (
            f'Job(interval={self.interval!r}, '
            f'func={self.func.__name__ if self.func else None})'
        )

    def every(self, interval: JobIntervalInType):
        self.interval = _parse_interval(interval)
        return self

    def do(self, func: JobFuncInType):
        self.func = _parse_func(func)
        return self


def every(interval: JobIntervalInType):
    return Job(interval=_parse_interval(interval))


def do(func: JobFuncInType):
    return Job(func=_parse_func(func))


class Plan:
    def __init__(self, iterable: Iterable[Job], /):
        self._jobs = list(iterable)
        self._run_state: Dict[int, Dict] = {
            i: {'last_run_time': None} for i, job in enumerate(self._jobs)
        }

    def run(self, onetime: bool = False):
        while True:
            for i, job in enumerate(self._jobs):
                run_state = self._run_state[i]
                last_run_time: dt.datetime = cast(dt.datetime, run_state['last_run_time'])
                is_successful: Union[bool, None] = None
                elapsed: Union[float, None] = None

                job_func = cast(Callable, job.func)
                job_interval = cast(dt.timedelta, job.interval)

                if last_run_time is None or dt.datetime.now() - last_run_time >= job_interval:
                    logger.info(f'Running {job} (last run: {last_run_time})')
                    try:
                        t_start = time.perf_counter()
                        job_func()
                        is_successful = True
                    except Exception:
                        is_successful = False
                        logger.exception(f'Crashed in {job} (ignored):')
                    finally:
                        elapsed = time.perf_counter() - t_start
                        run_state['last_run_time'] = dt.datetime.now()
                        logger.info(
                            ('Successful' if is_successful else 'Failed') + f' ({elapsed}s elapsed).'
                        )

            if onetime:
                break

            time.sleep(0.1)

    def __repr__(self):
        return repr(self._jobs)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Plan):
            raise TypeError(f'Cannot compare {type(self)} with {type(__o)}.')
        return self._jobs == __o._jobs


def take(*jobs: Job):
    return Plan(jobs)


if __name__ == '__main__':
    def f1():
        print('Making F1')

    def f2():
        print('Making F2')

    take(
        every('2s').do(f1),
        do(f2).every('3s'),
    ).run()
