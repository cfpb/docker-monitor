import configparser
from unittest import TestCase, mock

from docker.models.containers import Container
from docker_monitor.policy import ContainerPolicy, PolicyCheck
from docker_monitor.checks import ActiveBuildCheck


class ActiveBuildCheckTestCase(TestCase):
    def setUp(self):
        self.policy = ContainerPolicy(configparser.ConfigParser())

    def test_active_build_check(self):
        mock_container = mock.MagicMock(spec=Container)
        self.assertTrue(ActiveBuildCheck(self.policy, {})(mock_container))
