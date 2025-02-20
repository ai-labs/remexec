from __future__ import annotations

import re
import sys
import json

from io import StringIO
from pathlib import Path

import fabric


class Commands:
    RETRY_THRESHOLD: int = 3

    EXISTING_CONTAINER_PATTERN = re.compile(r'The container name .* is already in use by container "(.*)"')

    container: str | None = None

    def __init__(
        self,
        cxn: fabric.Connection,
        *,
        name: str | None = None,
        image: str | None = None,
    ) -> None:
        self.cxn = cxn

        if name is None:
            name = "ailabs.remexec"
        self.name = name

        if image is None:
            image = f"python:{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.image = image

    def start(self) -> fabric.Result:
        command = f'docker run --rm --name {self.name} --detach {self.image} bash -c "while true; do sleep 60; done"'
        result = self.cxn.run(command, hide=True, warn=True)

        if result.ok:
            self.container = result.stdout.strip()

        elif match := re.search(self.EXISTING_CONTAINER_PATTERN, result.stderr):
            self.container = match.group(1)

        else:
            message = f"Unknown error at container start up: {result.stderr}"
            raise RuntimeError(message)

        return result

    def stop(self) -> fabric.Result:
        command = f"docker container inspect {self.name}"
        result = self.cxn.run(command, hide=True, warn=True)

        if result.ok:
            self.container = json.loads(result.stdout)[0]["Id"]

        command = f"docker stop {self.container}"
        result = self.cxn.run(command, hide=True, warn=True)

        return result

    def __call__(self, command: str, **kwargs) -> fabric.Result:
        command = f"docker exec --interactive {self.container} {command}"
        result = self.cxn.run(command, **({"hide": True, "warn": True, "timeout": 60} | kwargs))

        return result


class Executor:
    def __init__(
        self,
        cxn: fabric.Connection,
        *,
        container: str | None = None,
        image: str | None = None,
    ) -> None:
        self.commands, self.cxn = Commands(cxn, name=container, image=image), cxn

    def __enter__(self) -> Executor:
        if not self.cxn.run("which docker", hide=True, warn=True).ok:
            message = "Can not find docker on the remote machine"
            raise RuntimeError(message)

        self.commands.start()
        return self

    def __exit__(self, *_) -> None:
        self.commands.stop()
        self.cxn.close()

    def shell(self, source: str | Path, /, **kwargs) -> fabric.Result:
        with StringIO(source) if isinstance(source, str) else source.open() as buffer:
            return self.commands("bash -", **(kwargs | {"in_stream": buffer}))

    def python(self, source: str | Path, /, **kwargs) -> fabric.Result:
        with StringIO(source) if isinstance(source, str) else source.open() as buffer:
            return self.commands("python -", **(kwargs | {"in_stream": buffer}))
