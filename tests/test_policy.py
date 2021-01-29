import logging
import configparser

from docker.models.containers import Container
from unittest import TestCase, mock

from docker_monitor.policy import (
    import_from_string,
    ContainerPolicy,
    PolicyCheck,
)


class PassingCheck(PolicyCheck):
    description = "test case check that passes"

    def __call__(self, container):
        return self.PASS


class PassingFastCheck(PolicyCheck):
    description = "test case check that passes fast"

    def __call__(self, container):
        return self.PASS_FAST


class FailingCheck(PolicyCheck):
    description = "test case check that fails"

    def __call__(self, container):
        return self.FAIL


class PolicyTestCase(TestCase):
    def setUp(self):
        self.config = configparser.ConfigParser()
        self.policy = ContainerPolicy(configparser.ConfigParser())

    def test_policycheck_call_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            PolicyCheck(self.policy, {})(None)

    def test_import_from_string(self):
        callable_obj = import_from_string(
            "docker_monitor.policy.import_from_string"
        )
        self.assertEqual(callable_obj, import_from_string)

        with self.assertRaises(ImportError):
            import_from_string("not_a_dotted__path")

        with self.assertRaisesRegex(ImportError, "[a-z] is not defined in .*"):
            import_from_string("docker_monitor.policy.nonexistent")

    def test_container_policy_parse_checks(self):
        self.config["tests.test_policy.PassingCheck"] = {"foo": "bar"}
        self.config["logging"] = {}
        self.config["policy"] = {}
        checks = self.policy.get_checks(self.config)
        self.assertEqual(len(checks), 1)
        self.assertEqual(checks[0].__class__, PassingCheck)
        self.assertEqual(checks[0].config["foo"], "bar")

    def test_container_policy_check(self):
        mock_container = mock.MagicMock(spec=Container)

        check_pass = PassingCheck(self.policy, {})
        check_pass_fast = PassingFastCheck(self.policy, {})
        check_fail = FailingCheck(self.policy, {})

        # The first check should fail and cause general failure
        self.policy.checks = [check_fail, check_pass]
        self.assertFalse(self.policy.check(mock_container))

        # The second check should fail and cause general failure
        self.policy.checks = [check_pass, check_fail]
        self.assertFalse(self.policy.check(mock_container))

        # The first check should pass fast and cause general passing
        self.policy.checks = [check_pass_fast, check_fail]
        self.assertTrue(self.policy.check(mock_container))

        # The check should pass and cause general passing
        self.policy.checks = [check_pass]
        self.assertTrue(self.policy.check(mock_container))

    def test_warn(self):
        mock_container = mock.MagicMock(spec=Container)
        with self.assertLogs(level=logging.WARNING) as logs:
            self.policy.warn(mock_container)
        self.assertEqual(len(logs.records), 1)
        self.assertRegex(logs.output[0], "failed policy checks")

    def test_kill(self):
        mock_container = mock.MagicMock(spec=Container)
        with self.assertLogs(level=logging.ERROR) as logs:
            self.policy.kill(mock_container)
        self.assertEqual(len(logs.records), 1)
        self.assertRegex(logs.output[0], "Killing")
        assert mock_container.kill.called
