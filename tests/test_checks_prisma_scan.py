import configparser
from unittest import TestCase, mock

from docker.models.containers import Container
from docker_monitor.policy import ContainerPolicy, PolicyCheck
from docker_monitor.checks import PrismaScanCheck


class PrismaScanCheckTestCase(TestCase):
    def setUp(self):
        self.policy = ContainerPolicy(configparser.ConfigParser())
        self.config = {
            "twistcli_path": "path_to_twistcli",
            "url": "http://myurl",
            "token": "mytoken",
        }

    @mock.patch("subprocess.getoutput")
    def test_prisma_scan_call(self, mock_subprocess_getoutput):
        check = PrismaScanCheck(self.policy, self.config)
        mock_container = mock.MagicMock(spec=Container)
        mock_subprocess_getoutput.side_effect = [
            """
Compliance found for image: total - 2, critical - 0, high - 2, medium - 0, low - 0
Compliance threshold check results: PASS
            """,
            """
Compliance found for image: total - 2, critical - 0, high - 2, medium - 0, low - 0
Compliance threshold check results: FAIL
            """,
        ]
        self.assertTrue(check(mock_container))
        self.assertFalse(check(mock_container))

    @mock.patch("subprocess.getoutput")
    def test_prisma_scan_call_no_config(self, mock_subprocess_getoutput):
        mock_container = mock.MagicMock(spec=Container)

        check = PrismaScanCheck(
            self.policy, {"twistcli_path": None, "url": None, "token": None}
        )
        with self.assertRaises(ValueError):
            check(mock_container)

        check = PrismaScanCheck(
            self.policy, {"twistcli_path": "", "url": "", "token": ""}
        )
        with self.assertRaises(ValueError):
            check(mock_container)

        check = PrismaScanCheck(
            self.policy, {"twistcli_path": "apath", "url": None, "token": ""}
        )
        with self.assertRaises(ValueError):
            check(mock_container)

        check = PrismaScanCheck(
            self.policy, {"twistcli_path": "apath", "url": "aurl", "token": ""}
        )
        with self.assertRaises(ValueError):
            check(mock_container)
