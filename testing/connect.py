from textwrap import dedent

from rich import print  # noqa: A004
from fabric import Connection

from ailabs.remexec import Executor


with Executor(Connection("108.181.157.13", user="administrator")) as executor:
    # Context manager checks if docker is available and creates runtime container if it does not exist.
    # Existing container will not be re-created, use manual `stop()`/`start()` methods of the
    # `executor.commands` object for that. On context manager exit, runtime container will be destroyed.

    # Execution in both `shell` and `python` modes performed by piping source code to STDIN.
    # No TTY/PTY is available in this runtime, so utilities like `nano` will throw an error
    # like "Standard input is not a terminal" or similar, or simply will hang.

    # There is a timeout for command to finish, 60 seconds by default. It can be disabled/changed
    # by passing `timeout` keyword argument to the `shell()`/`python()` functions.

    # First position-only argument to these functions - `source` - may be a string or
    # a file-like object opened in text reading mode.

    # Both functions will return a `fabric.Result` object with return code, stdout and stderr available.

    result = executor.python(
        dedent(
            """
            import os
            import sys


            print(os.uname())
            print(__name__, file=sys.stderr)

            1 / 0
            """
        )
    )

    print(result)

    result = executor.shell(
        dedent(
            """
            if command -v -- uname > /dev/null 2>&1; then
                uname -a
            else
                echo "uname command not found"
            fi
            """
        )
    )

    print(result)

    result = executor.shell("pip install pandas")
    print(result)

    result = executor.python("import pandas; print(pandas)")
    print(result)

    result = executor.shell("apt update; apt install nano; nano")
    print(result)
