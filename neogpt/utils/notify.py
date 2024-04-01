import platform
import subprocess

from plyer import notification


def notify(
    title,
    message,
    timeout=10,
    ticker="NeoGPT says Hi!",
    app_name="NeoGPT",
    app_icon="path/to/icon.icns",
    toast=False,
):
    """
    Show a desktop notification to the user

    Parameters:
    title (str): notification title - required
    message (str): notification message - required
    timeout (int): timeout in seconds to hide the notification. default value is 10 - optional
    app_name (str): name of the app - optional
    app_icon (str): path to the icon of the app - optional

    The function uses osascript for macOS and plyer for other platforms.
    """
    if platform.system() == "Darwin":  # Check if the platform is macOS
        osascript_cmd = [
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}" sound name "default"',
        ]
        subprocess.run(osascript_cmd)
    else:
        notification.notify(
            title=title,
            message=message,
            app_name=app_name,
            app_icon=app_icon,
            timeout=timeout,
            toast=toast,
            # ticker=ticker
        )


# Test the notify function
# notify("NeoGPT", "Copied to clipboard!")
