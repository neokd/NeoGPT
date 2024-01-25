# def get_username() to get the current user name 
# def get_user_info() to return the current user name ,  shell name, os name, current working directory.
import os

def get_username():
    return os.getlogin()

def get_user_info():
    username = get_username()
    shell_name = os.getenv('SHELL')
    os_name = os.name
    cwd = os.getcwd()
    return username, shell_name, os_name, cwd
  
username, shell_name, os_name, cwd = get_user_info()
print("Username:", username)
print("Shell:", shell_name)
print("OS Name:", os_name)
print("Current Working Directory:", cwd)

