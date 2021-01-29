# CFPB Docker Monitor

The CFPB Docker Monitor is a command-line tool intended to be used to 
enforce a Docker policy that is defined by a combination of checks that 
pass or fail. 

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Built-in checks](#built-in-checks)
- [Getting help](#getting-help)
- [Getting involved](#getting-involved)
- [Licensing](#licensing)

## Installation

The CFPB Docker Monitor can be installed with [pip](https://pip.pypa.io/en/stable/):

```
pip install git+https://github.com/cfpb/docker-monitor
```

## Usage

Given a [config file](#configuration), the CFPB Docker Monitor can be run with:

```shell
docker_monitor -f /path/to/my_config.ini
```

It is intended to run automatically, periodically.

## Configuration

The CFPB Docker Monitor requires a config file that defines general policy 
configuration, logging, and the checks to be run and their configuration.
the checks to be run. 

```ini
[policy]
always_allow =

[logging]
log_file = /tmp/docker_monitor.log

[docker_monitor.checks.ActiveBuildCheck]

[docker_monitor.checks.RunningAsRootCheck]
allow_root = off

[docker_monitor.checks.RunningAsRootCheck]
allow_root = off

[docker_monitor.checks.PrismaScanCheck]
twistcli_path = 
token = 
url = 
```

### `policy` section

```ini
[policy]
# Image IDs listed here are always allowed, and the checks defined below will 
# not run on them.
always_allow =
```

- `always_allow` is a comma-separated list of Docker image ids that will 
  always be allowed. Checks will not run against these images, they will 
  always pass.

### `logging` section

```ini
[logging]
# The file to log output from each scan to
log_file = /tmp/docker_monitor.log
# The log level to use when writing logs out
level = 
```

- `log_file` is the file path to which output from each scan will be logged.
- `level` is the log level that will be writen to the file in `log_file`.

### Checks

Checks to be run as defined as sections in the config file, with the dotted 
Python module path to the check as the section name. For example:

```ini
[docker_monitor.checks.RunningAsRootCheck]
allow_root = off
```

This will cause the `RunningAsRootCheck` to be loaded from the 
`docker_monitor.checks` Python module, and run on Docker containers with 
the configuration `allow_root = off`.

Checks that do not have any configuration can be loaded by simply adding a 
section with their dotted Python path and no additional settings within 
the section. For example:

```ini
[docker_monitor.checks.ActiveBuildCheck]
```

Checks are run in the order in which they're defined in the config file. If 
you want a check to run before another check, define it before that check.


## Built-in checks

The CFPB Docker Monitor includes several built-in checks that can be run:

### `docker_monitor.checks.ActiveBuildCheck`

This will check to see if the Docker container is actively building an image.

If it is, this check will pass fast, meaning any checks defined after it will  
not be run. This check is intended to exempt Docker containers that are 
building new images from checks that are defined after it.

```ini
[docker_monitor.checks.ActiveBuildCheck]
```

### `docker_monitor.checks.ActiveBuildCheck`

This will check to see if the Docker container is set to run as root by 
default. 

```ini
[docker_monitor.checks.RunningAsRootCheck]
allow_root = off
```

### `docker_monitor.checks.PrismaScanCheck`

This will check to see if the image a Docker container is running passes a 
Prisma compliance threshold when scanned. 

This check uses the twistcli command-line tool, combined with the token and 
URL, to submit the image for scanning and wait for results. 

If the results report "Compliance threshold check results: PASS", then the 
check passes.

Any complaince thresholds must be configured in Prisma Cloud.

```ini
[docker_monitor.checks.PrismaScanCheck]
twistcli_path = 
token = 
url = 
```

## Defining new checks

Checks are classes that inherit from `docker_monitor.policy.PolicyCheck`
whose instances are callable with a `__call__` method that takes a [Docker 
container](https://docker-py.readthedocs.io/en/stable/containers.html) as the 
argument and determines whether the container's image passes the check.

Checks can return:

- `self.PASS`
- `self.PASS_FAST`
- `self.FAIL`

```python
from docker_monitor.policy import PolicyCheck


class MyPolicyCheck(PolicyCheck):
    description = "my custom policy check"

    def __call__(self, container):
        if self.config["pass"] == "pass":
            return self.PASS
        elif self.config["pass"] == "past fast":
            return self.PASS_FAST
        return self.FAIL
```


## Getting help

Please add issues to the [issue tracker](https://github.com/cfpb/docker-monitor/issues).

## Getting involved

General instructions on _how_ to contribute can be found in [CONTRIBUTING](CONTRIBUTING.md).

## Licensing
1. [TERMS](TERMS.md)
2. [LICENSE](LICENSE)
3. [CFPB Source Code Policy](https://github.com/cfpb/source-code-policy/)
