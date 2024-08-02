import os
import multiprocessing
import sys
import time
from urllib.parse import urlparse, urlunparse

from colorama import Fore, Style, Back
from flaresolverr.flaresolverr import run
import requests

from sylva import __user_agent__
from sylva.config import config
from sylva.easy_logger import LogLevel, loglevel, NoColor


flaresolverr_base_headers:dict[str, str] = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': __user_agent__,
}


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor


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
    def __init__(self, host: str = os.environ.get('HOST', '0.0.0.0'), port: int = None):
        self.server_host: str = host
        self.server_port: int = port if port is not None else 54011 # TODO Change to 0 when dynamic added to flaresolverr
        self.__stop_event: multiprocessing.Event = multiprocessing.Event()
        self.__server_process: multiprocessing.Process = multiprocessing.Process(
            target=self._start_async_server, args=(self.__stop_event,)
        )
        self.primary_proxy_url: str|None = None
        self.primary_session_id: str|None = None


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
            self.server_host = self.server_host if self.server_host != '0.0.0.0' else '127.0.0.1'
            self.primary_proxy_url = f'http://{self.server_host}:{self.server_port}/v1'

            for i in range(5):
                if test_if_flaresolverr_online(proxy_url=self.primary_proxy_url):
                    break
                time.sleep(2)
            else:
                raise Exception('Failed to start primary FlareSolverr session')


    def start_primary_session(self) -> str:
        if not test_if_flaresolverr_online(proxy_url=self.primary_proxy_url):
            raise Exception('FlareSolverr is not online')
        
        if self.primary_session_id:
            return self.primary_session_id

        response = requests.post(
            url=self.primary_proxy_url,
            json={
                'cmd': 'sessions.create',
            },
        )

        if response.status_code != 200 or 'message' not in response.json():
            raise Exception('Unable to properly communicate with FlareSolverr')
        if response.json()['message'] != 'Session created successfully.':
            raise Exception('Failed to create primary session')

        self.primary_session_id = response.json()['session']

        return self.primary_session_id


    def destroy_all_sessions(self):
        if not test_if_flaresolverr_online(proxy_url=self.primary_proxy_url):
            raise Exception('FlareSolverr is not online')

        response = requests.post(
            url=self.primary_proxy_url,
            json={
                'cmd': 'sessions.list',
            },
        )
        if response.status_code != 200:
            raise Exception('Unable to properly communicate with FlareSolverr')

        sessions: list[str] = response.json()['sessions']

        for session in sessions:
            response = requests.post(
                url=self.primary_proxy_url,
                json={
                    'cmd': 'sessions.destroy',
                    'session': session,
                },
            )
            if response.status_code != 200:
                raise Exception('Unable to properly communicate with FlareSolverr')
            if response.json()['msg'] != 'Session destroyed successfully.':
                raise Exception('Failed to destroy primary session')
