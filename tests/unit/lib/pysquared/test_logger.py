import pytest

from lib.pysquared.logger import Logger


@pytest.fixture
def logger():
    return Logger()


def test_debug_log(capsys, logger):
    logger.debug("This is a debug message", blake="jameson")
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "This is a debug message" in captured.out
    assert '"blake": "jameson"' in captured.out
