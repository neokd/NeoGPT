import getpass
import os


def get_username():
    return getpass.getuser()


def get_user_info():
    username = get_username()
    shell_name = os.getenv("SHELL")
    os_name = os.name
    cwd = os.getcwd()
    return username, shell_name, os_name, cwd


# username, shell_name, os_name, cwd = get_user_info()
# print("Username:", username)
# print("Shell:", shell_name)
# print("OS Name:", os_name)
# print("Current Working Directory:", cwd)
