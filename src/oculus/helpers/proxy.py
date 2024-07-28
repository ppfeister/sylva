import os
import multiprocessing
import sys
import time

from colorama import Fore, Style, Back
from flaresolverr.flaresolverr import run

from oculus.config import config
from oculus.easy_logger import LogLevel, loglevel, NoColor


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor


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
            if loglevel >= LogLevel.INFO.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Starting FlareSolverr...')
            while not stop_event.is_set():
                run(server_host=self.server_host, server_port=self.server_port)
        except Exception as e:
            if loglevel >= LogLevel.INFO.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Unable to start FlareSolverr, proceeding without it')
        else:
            if loglevel >= LogLevel.INFO.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Started FlareSolverr on {self.server_host}:{self.server_port}')

    def stop(self):
        """
        Stop the server by setting the stop event and joining the process.
        """
        if self.__server_process.is_alive():
            if loglevel >= LogLevel.DEBUG.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Stopping FlareSolverr...')
            self.__stop_event.set()
            self.__server_process.terminate()
            if not self.__server_process.is_alive():
                if loglevel >= LogLevel.DEBUG.value:
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Stopped FlareSolverr')
            else:
                if loglevel >= LogLevel.INFO.value:
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Something went wrong terminating FlareSolverr')
        else:
            if loglevel >= LogLevel.DEBUG.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Attempted to stop FlareSolverr, but it was not running')

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