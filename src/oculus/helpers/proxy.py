import os
import multiprocessing
import sys
import time

from flaresolverr.flaresolverr import run


class ProxySvc:
    def __init__(self, host: str = os.environ.get('HOST', '0.0.0.0'), port: int = None):
        self.server_host: str = host
        self.server_port: int = port if port is not None else 54011 # TODO Change to 0 when dynamic added to flaresolverr
        self.__stop_event: multiprocessing.Event = multiprocessing.Event()
        self.__server_process: multiprocessing.Process = multiprocessing.Process(
            target=self._start_async_server, args=(self.__stop_event,)
        )

    def __del__(self):
        self.stop()

    def _start_async_server(self, stop_event):
        """
        Start the FlareSolverr server asynchronously and monitor the stop event.
        """
        sys.stdout = open(os.devnull, 'w')
        try:
            while not stop_event.is_set():
                run(server_host=self.server_host, server_port=self.server_port)
        except Exception as e:
            print(f"Exception in _start_async_server: {e}")

    def stop(self):
        """
        Stop the server by setting the stop event and joining the process.
        """
        if self.__server_process.is_alive():
            self.__stop_event.set()
            self.__server_process.join()
            print("Server stopped.")

    def start(self):
        """
        Start the server process.
        """
        if not self.__server_process.is_alive():
            self.__stop_event.clear()  # Reset the stop event in case it was set before
            self.__server_process = multiprocessing.Process(
                target=self._start_async_server, args=(self.__stop_event,)
            )
            self.__server_process.start()