import logging
from abc import ABC
from importlib import import_module


def import_from_string(import_str):
    try:
        module_name, callable_name = import_str.rsplit(".", 1)
    except ValueError as err:
        raise ImportError(f"{import_str} isn't a valid module path") from err

    module = import_module(module_name)

    try:
        return getattr(module, callable_name)
    except AttributeError as err:
        raise ImportError(
            f"{callable_name} is not defined in {module_name}"
        ) from err


class ContainerPolicy:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.checks = self.get_checks(config)

    def get_checks(self, config):
        return [
            import_from_string(section)(self, config[section])
            for section in config.sections()
            if section not in ("logging", "policy")
        ]

    def check(self, container):
        """Run all checks against the container

        Checks return one of the values from Result, above.

        If a check returns Result.FAIL, this method will return False
        immediately.

        If a check returns Result.PASS_FAST, this method will immediately
        return True, skipping all subsequent checks.

        If a check returns Result.PASS, this method will continue with
        subsequent checks.
        """
        for check in self.checks:
            # Run the check on the container
            result = check(container)

            if result <= PolicyCheck.FAIL:
                # Log the failure and return False. All failures result in an
                # immediate return.
                self.logger.error(
                    f"{container.name} failed check, {check.description}"
                )
                return False

            elif result >= PolicyCheck.PASS:
                # Log that the check passed
                self.logger.info(
                    f"{container.name} passed check, {check.description}"
                )

                # If the check was a "pass fast", then we skip all subsequent
                # checks and simply return True.
                if result == PolicyCheck.PASS_FAST:
                    return True

        # If we made it this far, all checks passed
        return True

    def warn(self, container):
        """ Log a warning that the given container failed policy checks """
        self.logger.warning(f"{container.name} failed policy checks")

    def kill(self, container):
        """ Kill the given container """
        self.logger.error(f"Killing {container.name}")
        container.kill()


class PolicyCheck(ABC):
    description = "policy check"

    FAIL = 0
    PASS = 1
    PASS_FAST = 2

    def __init__(self, policy, config):
        self.policy = policy
        self.config = config

    def __call__(self, container):
        raise NotImplementedError
