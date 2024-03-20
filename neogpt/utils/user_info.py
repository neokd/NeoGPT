import getpass
import os
import platform


def get_username():
    return getpass.getuser()


def get_user_info():
    username = get_username()
    shell_name = os.getenv("SHELL")
    os_name = platform.platform()
    python_version = platform.python_version()
    cwd = os.getcwd()
    return username, shell_name, os_name, python_version, cwd
