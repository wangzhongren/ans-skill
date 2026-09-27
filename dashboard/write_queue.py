"""Bounded, single-threaded execution of cloud Dashboard writes."""
from concurrent.futures import Future
from queue import Full, Queue
from threading import Thread


class WriteQueueBusy(RuntimeError):
    pass


class WriteQueue:
    def __init__(self, capacity=128):
        self.queue = Queue(maxsize=capacity)
        Thread(target=self._run, name='ans-dashboard-writer', daemon=True).start()

    def _run(self):
        while True:
            future, function, args = self.queue.get()
            try:
                if future.set_running_or_notify_cancel():
                    future.set_result(function(*args))
            except BaseException as error:
                future.set_exception(error)
            finally:
                self.queue.task_done()

    def call(self, function, *args):
        future = Future()
        try:
            self.queue.put_nowait((future, function, args))
        except Full as error:
            raise WriteQueueBusy('Dashboard write queue is full; retry shortly') from error
        return future.result()
