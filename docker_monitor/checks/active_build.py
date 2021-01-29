import logging

from docker_monitor.policy import PolicyCheck


logger = logging.getLogger(__name__)


class ActiveBuildCheck(PolicyCheck):
    description = "is actively building"

    def __call__(self, container):
        # return self.PASS_FAST
        return self.PASS
