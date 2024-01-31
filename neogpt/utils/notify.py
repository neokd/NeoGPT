import asyncio
from plyer import notification

async def notify(title, message, timeout=10):
    """
    Show a desktop notification to the user.

    Parameters:
    title: notification title - required
    message: notification message - required
    timeout: timeout in seconds to hide the notification. Default value is 10 - optional
    """
    notification.notify(
        title=title,
        message=message,
        timeout=timeout
    )
    await asyncio.sleep(timeout)  # Wait for the specified timeout

## test
await notify('test', 'this is a test notification')
