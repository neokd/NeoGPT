import asyncio
from plyer import notification

async def notify(title, message, timeout=10, ticker = 'NeoGPT says Hi!', app_name='NeoGPT', app_icon="docs/assets/icon.ico",toast=False):
    """
    Show a desktop notification to user

    Parameters:
    title (str): notification title - required
    message (str): notification message - required
    timeout (int): timeout in seconds to hide the notification. default value is 10 - optional
    app_name (str): name of the app - optional
    app_icon (str): path to the icon of the app - optional

    The function uses the plyer library to send desktop notifications. Plyer is a Python library 
    for accessing features of your hardware / platforms.
    """
    # Send a notification with the given title and message
    notification.notify(
        title=title, 
        message=message, 
        app_name=app_name, 
        app_icon=app_icon, 
        timeout=timeout,
        toast=toast,
        #ticker=ticker
    )
    # Sleep for the duration of the timeout, then continue
    await asyncio.sleep(timeout)

# Test the notify function
# asyncio.run(notify('test', 'this is a test notification'))