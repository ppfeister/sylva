import multiprocessing
import os
import subprocess
import sys
import time
from multiprocessing.synchronize import Event as EventType
from urllib.parse import urlparse, urlunparse

import requests
from colorama import Back, Fore, Style

from .. import __user_agent__
from ..config import config
from ..easy_logger import LogLevel, NoColor, loglevel
from .flaresolverr.flaresolverr import run  # type: ignore[import-not-found, unused-ignore] # problematic during ci

flaresolverr_base_headers:dict[str, str] = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': __user_agent__,
}


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor  # type: ignore[assignment] # TODO: Check if still works under new layout


def test_if_flaresolverr_online(proxy_url:str) -> bool:
    """Test if the FlareSolverr proxy server is online

    Keyword Arguments:
        proxy_url {str} -- The URL of the proxy server to test

    Returns:
        bool -- True if the proxy server is online, False otherwise
    """
    parsed_url = urlparse(proxy_url)
    proxy_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

    try:
        flaresolverr_response_test = requests.get(url=proxy_url, headers=flaresolverr_base_headers)
    except requests.exceptions.ConnectionError:
        return False

    if flaresolverr_response_test.status_code != 200:
        return False
    if flaresolverr_response_test.json()['msg'] != 'FlareSolverr is ready!':
        return False

    return True


class ProxySvc:
    def __init__(self, host: str = os.environ.get('HOST', '0.0.0.0'), port: int|None = None):
        self.server_host: str = host
        self.server_port: int = port if port is not None else 54011 # TODO Change to 0 when dynamic added to flaresolverr  # fmt: skip # noqa: E501
        self.__stop_event: EventType = multiprocessing.Event()
        self.__server_process: multiprocessing.Process = multiprocessing.Process(
            target=self._start_async_server, args=(self.__stop_event,)
        )
        self.primary_proxy_url: str|None = None
        self.primary_session_id: str|None = None

        # FIXME: Remove when FlareSolverr nonsense is fixed
        if os.environ.get('SYLVA_ENV', 'tty') == 'docker':
            def _call_flaresolverr_module() -> None:
                subprocess.call(['python', '-u', '/app/flaresolverr.py'])
            self.server_host = '127.0.0.1'
            self.server_port = 8191
            self.__server_process = multiprocessing.Process(
                target=_call_flaresolverr_module
            )


    def __del__(self) -> None:
        self.stop()


    def _start_async_server(self, stop_event: EventType) -> None:
        """
        Start the FlareSolverr server asynchronously and monitor the stop event.
        """
        sys.stdout = open(os.devnull, 'w')
        try:
            if loglevel >= LogLevel.INFO.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Starting FlareSolverr...')
            while not stop_event.is_set():
                run(server_host=self.server_host, server_port=self.server_port)
        except Exception:
            if loglevel >= LogLevel.INFO.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Unable to start FlareSolverr, proceeding without it')  # fmt: skip # noqa: E501
        else:
            if loglevel >= LogLevel.INFO.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Started FlareSolverr on {self.server_host}:{self.server_port}')  # fmt: skip # noqa: E501


    def stop(self) -> None:
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
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Something went wrong terminating FlareSolverr')  # fmt: skip # noqa: E501
        else:
            if loglevel >= LogLevel.DEBUG.value:
                print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Attempted to stop FlareSolverr, but it was not running')  # fmt: skip # noqa: E501


    def start(self) -> None:
        """
        Start the server process.
        """
        if not self.__server_process.is_alive():
            self.__stop_event.clear()  # Reset the stop event in case it was set before
            self.__server_process = multiprocessing.Process(
                target=self._start_async_server, args=(self.__stop_event,)
            )
            self.__server_process.start()
            self.server_host = self.server_host if self.server_host != '0.0.0.0' else '127.0.0.1'
            self.primary_proxy_url = f'http://{self.server_host}:{self.server_port}/v1'

            for i in range(6):
                if test_if_flaresolverr_online(proxy_url=self.primary_proxy_url):
                    break
                time.sleep(0.5)
            else:
                raise Exception('FlareSolverr failed to start for an unknown reason')


    def start_primary_session(self) -> str:
        if not test_if_flaresolverr_online(proxy_url=self.primary_proxy_url):  # type: ignore[arg-type]
            raise Exception('FlareSolverr is not online')

        if self.primary_session_id:
            return self.primary_session_id

        response = requests.post(
            url=self.primary_proxy_url,  # type: ignore[arg-type]
            json={
                'cmd': 'sessions.create',
            },
        )

        if response.status_code != 200 or 'message' not in response.json():
            raise Exception('Unable to properly communicate with FlareSolverr')
        if response.json()['message'] != 'Session created successfully.':
            raise Exception('Failed to create primary session')

        self.primary_session_id = response.json()['session']

        return self.primary_session_id  # type: ignore[return-value]


    def destroy_all_sessions(self) -> None:
        if not test_if_flaresolverr_online(proxy_url=self.primary_proxy_url):  # type: ignore[arg-type]
            raise Exception('FlareSolverr is not online')

        response = requests.post(
            url=self.primary_proxy_url,  # type: ignore[arg-type]
            json={
                'cmd': 'sessions.list',
            },
        )
        if response.status_code != 200:
            raise Exception('Unable to properly communicate with FlareSolverr')

        sessions: list[str] = response.json()['sessions']

        for session in sessions:
            response = requests.post(
                url=self.primary_proxy_url,  # type: ignore[arg-type]
                json={
                    'cmd': 'sessions.destroy',
                    'session': session,
                },
            )
            if response.status_code != 200:
                raise Exception('Unable to properly communicate with FlareSolverr')
            if response.json()['msg'] != 'Session destroyed successfully.':
                raise Exception('Failed to destroy primary session')
