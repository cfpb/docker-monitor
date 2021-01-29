import logging
import subprocess
import re

from docker_monitor.policy import PolicyCheck


logger = logging.getLogger(__name__)


class PrismaScanCheck(PolicyCheck):
    description = "Prisma compliance"

    def __call__(self, container):
        twistcli_path = self.config.get("twistcli_path")
        url = self.config.get("url")
        token = self.config.get("token")

        if not twistcli_path or not url or not token:
            raise ValueError(
                "PrismaScanCheck needs twistcli_path, url, and token "
                "configured."
            )

        image_id = container.image.short_id.split(":")[1]

        command = [
            twistcli_path,
            "images",
            "scan",
            "--token",
            token,
            "--address",
            url,
            image_id,
        ]

        command = (
            f"{twistcli_path} images scan --token {token} "
            f"--address {url} {image_id}"
        )

        logger.debug(f"Running command: {command}")
        results = subprocess.getoutput(command)
        logger.debug(f"Command output: {results}")

        if "Compliance threshold check results: PASS" in results:
            return self.PASS

        return self.FAIL
