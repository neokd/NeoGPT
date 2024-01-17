import asyncio
from desktop_notifier import DesktopNotifier

notifier = DesktopNotifier()

async def notify(title, message, timeout=10):
    """
    Show a desktop notification to user

    Parameter:
    title: notification title - required
    message: notification message - required
    timeout:  timeout in seconds to hide the notification. default value is 10 - optional 
    """
    n = await notifier.send(title=title, message=message)
    await asyncio.sleep(timeout)  
    await notifier.clear(n)  
    

## test 
## asyncio.run(notify('test', 'this is a test notification'))