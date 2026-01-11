"""
Collection of helper methods.
"""

from pathlib import Path
import sys
from time import sleep

from loguru import logger


def get_application_path(relative_path: str | None = None) -> str:
    """
    Gets the path the application is being run from.
    For the python version, this will be the project folder.
    For the executable, this will be the folder it is in.
    Use this for config & logs.

    Args:
        relative_path: An optional relative path that will get added to the result.

    Returns:
         An absolute version of the application path.
    """
    # '_MEIPASS' is set by pyinstaller
    if hasattr(sys, "_MEIPASS"):
        path = Path(sys.executable).parent.absolute()
    else:
        path = Path(__file__).parent.parent.absolute()

    if relative_path:
        return str(path / relative_path)

    return str(path)


def get_resource_path(relative_path: str | None = None):
    """
    Gets the path image resources are at.
    For the python version, this will be the project folder.
    For the executable, this will be a folder that's created in %APPDATA%.
    Use this for images.

    Args:
        relative_path: An optional relative path that will get added to the result.

    Returns:
        An absolute version of the resource path.
    """
    if hasattr(sys, "_MEIPASS"):
        path = Path(getattr(sys, "_MEIPASS")).absolute()
    else:
        path = Path(__file__).parent.parent.absolute()

    if relative_path:
        return str(path / relative_path)

    return str(path)


def is_version_string_newer(version_one: str, version_two: str):
    """
    Checks if version_one is newer than version_two.

    Args:
        version_one: The semantic version string to check.
        version_two: The semantic version string to check against.

    Returns:
        Whether version_one is newer than version_two.
    """
    try:
        version_one_parts = [int(part) for part in version_one.split(".")]
        version_two_parts = [int(part) for part in version_two.split(".")]
    except ValueError:
        logger.warning(
            f"We could not check version {version_one} against {version_two}. "
            f"Assuming the installed version ({version_two}) is newer."
        )
        return False

    version_part_amount = min(len(version_one_parts), len(version_two_parts))

    for i in range(version_part_amount):
        version_one_part = version_one_parts[i]
        version_two_part = version_two_parts[i]

        if version_one_part == version_two_part:
            continue

        return version_one_part > version_two_part

    return len(version_one_parts) > len(version_two_parts)


def get_major_version(version: str) -> int | None:
    """
    Extracts the major version component from a semantic version string.

    Args:
        version: The semantic version string to parse.

    Returns:
        The major version as an int, or None if it could not be parsed.
    """
    try:
        return int(version.split(".")[0])
    except (IndexError, ValueError):
        logger.warning(f"Could not parse major version from {version}.")
        return None


def raise_and_exit(error: str, exit_code: int = 1) -> None:
    """
    Raise the given text as an error and then exit the application

    Args:
        error: The error message to log before exiting.
        exit_code: The exit code to use when terminating the application. Defaults to 1.
    """
    logger.error(error)
    logger.warning("Due to an error, we are exiting Alune in 10 seconds. You can find all logs in alune-output/logs.")
    sleep(10)
    sys.exit(exit_code)
