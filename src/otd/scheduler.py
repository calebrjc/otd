from datetime import datetime, timedelta, timezone
import sched
import threading
from dataclasses import dataclass, field
from typing import Callable

from otd.log import LOGGER


@dataclass
class _Job:
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)


def _get_next_qhour_ts_utc() -> float:
    """Return the timestamp of the next quarter hour."""
    now = datetime.now()
    minutes_to_add = 15 - (now.minute % 15)
    next_qhour = now + timedelta(minutes=minutes_to_add)
    next_qhour = next_qhour.replace(second=0, microsecond=0)
    return next_qhour.timestamp()


def _get_current_time_ts_utc() -> float:
    return datetime.now(timezone.utc).timestamp()


class Scheduler:
    def __init__(self):
        self._thread = threading.Thread(target=self._run)
        self._event = threading.Event()
        self._scheduler = sched.scheduler(
            timefunc=_get_current_time_ts_utc,
            delayfunc=self._wait_for_event,
        )
        self._jobs: list[_Job] = []
        self._lock = threading.RLock()
        self._started = False

    def _schedule_job(self, func: _Job, when: float, priority: int = 1) -> None:
        LOGGER.info(f'Scheduling function "{func.function.__name__}()".')

        self._scheduler.enterabs(
            when,
            priority=priority,
            action=func.function,
            argument=func.args,
            kwargs=func.kwargs,
        )

    def _schedule_next_run(self) -> None:
        LOGGER.info("Scheduling the next run.")
        next_qhour = _get_next_qhour_ts_utc()

        # NOTE(Caleb): Don't allow the jobs list to change while scheduling
        with self._lock:
            for job in self._jobs:
                self._schedule_job(job, next_qhour)

        self._schedule_job(
            _Job(self._schedule_next_run),
            next_qhour,
            priority=2,
        )

        LOGGER.info("Finished scheduling the next run.")

    def _wait_for_event(self, timeout: float) -> None:
        self._event.wait(timeout=timeout)

    def _run(self) -> None:
        LOGGER.info("Running scheduler loop.")

        # NOTE(Caleb): Ensure all modifications happen either before the initial scheduling or after
        #              marking the scheduler as started. This prevents race conditions where a job
        #              can be added after the initial scheduling but before the scheduler starts,
        #              meaning that the job wouldn't execute until after the next run.
        with self._lock:
            self._schedule_next_run()
            self._started = True

        LOGGER.info("Initial scheduling complete. Scheduler marked as started.")

        while not self._event.is_set():
            if self._scheduler.empty():
                # NOTE(Caleb): No events to run, sleep for 15 seconds.
                self._event.wait(timeout=15)
                continue

            self._wait_for_event(1.0)
            self._scheduler.run(blocking=False)

        LOGGER.info("Exiting scheduler loop.")

    def _is_running(self) -> bool:
        return self._thread.is_alive()

    def start(self) -> None:
        if self._is_running():
            return

        LOGGER.info("Starting scheduler thread.")

        self._event = threading.Event()
        self._thread.start()

        LOGGER.info("Scheduler thread started.")

    def stop(self) -> None:
        if not self._is_running():
            return

        LOGGER.info("Stopping scheduler thread.")

        self._event.set()
        self._thread.join()

        LOGGER.info("Scheduler thread stopped.")

    def add_job(self, func: Callable, args: tuple = (), kwargs: dict = None) -> None:
        LOGGER.info(f'Adding function "{func.__name__}()" to the scheduler.')

        job = _Job(func, args=args or (), kwargs=kwargs or {})

        with self._lock:
            self._jobs.append(job)

            if self._started:
                self._schedule_job(job, _get_next_qhour_ts_utc())

        LOGGER.info(
            f'Added function "{job.function.__name__}()" to scheduler '
            f"({'scheduled' if self._started else 'not scheduled'})."
        )
