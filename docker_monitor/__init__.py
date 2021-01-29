import argparse
import configparser
import logging
import pathlib

import docker

from docker_monitor.policy import ContainerPolicy


# Check for containers, loop through
# - Check if running
# - - Yes, check for active build
# - - No, check with twistlock
# - - - Yes, has been scanned, parse result
# - - - No, scan image
# - - - - Parse result. Allowed?
# - - - - Yes, log and move on
# - - - - No, log and kill, create/append to log on user desktop


CONFIG_DEFAULTS = {
    "logging": {
        "log_file": "",
    },
    "policy": {
        "allow_root": "off",
        "always_allow": "",
        "action": "warn",  # "kill"
        "checks": """
            docker_monitor.checks.active_build
            docker_monitor.checks.running_as_root
            docker_monitor.checks.prisma_scan
        """,
    },
}


def setup_logging(verbosity, log_file=None):
    logger = logging.getLogger(__name__)
    logging.basicConfig()

    # Set logging level based on verbosity
    logger.setLevel(logging.ERROR - (min(verbosity, 3) * 10))

    if log_file is not None:
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s : %(levelname)s : %(name)s : %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def get_containers():  # pragma: no cover
    docker_client = docker.from_env()
    return docker_client.containers.list()


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Enforce Prisma Cloud Docker image policies locally"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="Verbose mode. Multiple -v options increases verbosity.",
    )
    parser.add_argument(
        "-f",
        "--config-file",
        type=pathlib.Path,
        action="store",
        required=True,
        help="Path to .ini config file",
    )
    parser.add_argument(
        "--enforce",
        dest="enforce",
        action="store_true",
        default=True,
        help="Enforce policy on containers, per configuration.",
    )
    parser.add_argument(
        "--no-enforce",
        dest="enforce",
        action="store_false",
        help="Check but do not enforce policy on containers",
    )
    args = parser.parse_args()

    # Get config
    config = configparser.ConfigParser()
    config.read_dict(CONFIG_DEFAULTS)
    config.read(args.config_file)

    # Set up logging and log file from configuration, if given
    setup_logging(args.verbosity, config["logging"]["log_file"])

    # Set up our policy checker
    policy = ContainerPolicy(config)

    # Get the list
    for container in get_containers():
        if not policy.check(container):
            if args.enforce:
                policy.kill(container)
            else:
                policy.warn(container)


if __name__ == "__main__":  # pragma: no cover
    main()
