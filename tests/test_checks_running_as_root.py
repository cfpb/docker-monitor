import configparser
from unittest import TestCase, mock

from docker.models.containers import Container
from docker_monitor.policy import ContainerPolicy, PolicyCheck
from docker_monitor.checks import RunningAsRootCheck


class RunningAsRootCheckTestCase(TestCase):
    def setUp(self):
        self.policy = ContainerPolicy(configparser.ConfigParser())

    def test_running_as_root_check(self):
        mock_container = mock.MagicMock(spec=Container)

        # Fail if user is empty (default is root)
        mock_container.attrs = {"Config": {"User": ""}}
        self.assertEqual(
            RunningAsRootCheck(self.policy, {})(mock_container),
            PolicyCheck.FAIL,
        )

        # Pass if user is empty (default is root) but we allow root
        mock_container.attrs = {"Config": {"User": ""}}
        self.assertEqual(
            RunningAsRootCheck(self.policy, {"allow_root": True})(
                mock_container
            ),
            PolicyCheck.PASS,
        )

        # Pass if the user is not empty and is not "root"
        mock_container.attrs = {"Config": {"User": "apache"}}
        self.assertEqual(
            RunningAsRootCheck(self.policy, {})(mock_container),
            PolicyCheck.PASS,
        )

        # Pass if we're set to allow root in configuration
        self.assertEqual(
            RunningAsRootCheck(self.policy, {"allow_root": True})(
                mock_container
            ),
            PolicyCheck.PASS,
        )
