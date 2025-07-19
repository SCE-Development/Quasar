import time
import logging

class MockPrinter():
    _instance = None
    _current_print_id_num = 0
    _jobs = {}
    _queue = []

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance
    
    def get_job_status(self, id: str) -> str:
        if id in self._jobs:
          return self._jobs[id]
        else:
           return "PRINTED"
    
    def remove_job(self, id: str) -> None:
        if id in self._jobs:
          self._jobs.pop(id, None)

    def lp(self) -> str:
        print_id = "HP_LaserJet_p2015dn_Right-" + str(self._current_print_id_num)
        self._current_print_id_num += 1
        self._jobs[print_id] = "PENDING"
        self._queue.append(print_id)
        return print_id

    def update(self) -> None:
      while True: 
          time.sleep(10)

          if self._queue.__len__() == 0:
              continue

          self._jobs[self._queue[0]] = "PRINTED"
          self._queue.pop(0)

    def log(self) -> None:
        while True:
            time.sleep(3)
            logging.info("-----------------")
            logging.info(f"jobs: {self._jobs}")
            logging.info(f"queue: {self._queue}")
