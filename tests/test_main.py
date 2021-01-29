import logging
import os
import tempfile
from unittest import TestCase

from docker_monitor import setup_logging


class MainTestCase(TestCase):
    def test_setup_logging_verbosity(self):
        logger = logging.getLogger("docker_monitor")

        setup_logging(0)
        with self.assertLogs() as logs:
            logger.debug("debug message")
            logger.info("info message")
            logger.warning("warning message")
            logger.error("error message")
        self.assertEqual(len(logs.records), 1)

        setup_logging(1)
        with self.assertLogs() as logs:
            logger.debug("debug message")
            logger.info("info message")
            logger.warning("warning message")
            logger.error("error message")
        self.assertEqual(len(logs.records), 2)

        setup_logging(2)
        with self.assertLogs() as logs:
            logger.debug("debug message")
            logger.info("info message")
            logger.warning("warning message")
            logger.error("error message")
        self.assertEqual(len(logs.records), 3)

        setup_logging(3)
        with self.assertLogs() as logs:
            logger.debug("debug message")
            logger.info("info message")
            logger.warning("warning message")
            logger.error("error message")
        self.assertEqual(len(logs.records), 4)

    def test_setup_logging_log_file(self):
        logger = logging.getLogger("docker_monitor")
        log_file, log_file_path = tempfile.mkstemp(text=True)

        setup_logging(2)
        self.assertEqual(len(logger.handlers), 0)

        setup_logging(0, log_file=log_file_path)
        self.assertEqual(len(logger.handlers), 1)

        os.unlink(log_file_path)

    def test_main(self):
        pass
