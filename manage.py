#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks for the Django application.

    This function sets the default settings module for Django and attempts
    to import the necessary management command execution function. If the
    import fails, it raises an ImportError with a descriptive message.
    Finally, it executes the command line utility for Django with the
    provided arguments.

    Raises:
        ImportError: If Django cannot be imported, indicating that it may not
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
