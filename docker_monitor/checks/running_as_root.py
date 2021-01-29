import logging

from docker_monitor.policy import PolicyCheck


logger = logging.getLogger(__name__)


class RunningAsRootCheck(PolicyCheck):
    description = "is running as root"

    def __call__(self, container):
        if not self.config.get("allow_root", False):
            if container.attrs["Config"]["User"] in ("", "root"):
                return self.FAIL
        return self.PASS
