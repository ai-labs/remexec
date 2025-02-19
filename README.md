## Remote execution library for LLM agents

This library allows to execute Pyhton/Bash code on the machine with Docker available. Machine may be local or remote.

Implemented as a manager object which keeps track on the runtime container and proxies commands into it. The exact connection is handled by [Fabric](https://www.fabfile.org/).

### Installation

#### Via SSH:

Production mode:

```shell
pip install ailabs.remexec@git+ssh://git@github.com/ai-labs/remexec.git
```

Development mode:

```shell
pip install ailabs.remexec[dev]@git+ssh://git@github.com/ai-labs/remexec.git
```

### Via HTTPS:

Production mode:

```shell
pip install ailabs.remexec@git+https://github.com/ai-labs/remexec.git
```

Development mode:

```shell
pip install ailabs.remexec[dev]@git+https://github.com/ai-labs/remexec.git
```

For more details on installing from GitHub see [this](https://stackoverflow.com/a/13754517) answer.


### Usage

See [this](testing/connect.py) file for example usage. For connection details see [Fabric](https://docs.fabfile.org/en/latest/api/connection.html) documentation.