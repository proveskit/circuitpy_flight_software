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


def test_info_log(capsys, logger):
    logger.info("This is a info message!!", foo="bar")
    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "This is a info message!!" in captured.out
    assert '"foo": "bar"' in captured.out


def test_warning_log(capsys, logger):
    logger.warning(
        "This is a warning message!!??!", boo="bar", pleiades="maia", cube="sat"
    )
    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "This is a warning message!!??!" in captured.out
    assert '"boo": "bar"' in captured.out
    assert '"pleiades": "maia"' in captured.out
    assert '"cube": "sat"' in captured.out


def test_error_log(capsys, logger):
    logger.error("This is an error message", hee="haa", pleiades="five", please="work")
    captured = capsys.readouterr()
    assert "ERROR" in captured.out
    assert "This is an error message" in captured.out
    assert '"hee": "haa"' in captured.out
    assert '"pleiades": "five"' in captured.out
    assert '"please": "work"' in captured.out


def test_critical_log(capsys, logger):
    logger.critical(
        "THIS IS VERY CRITICAL",
        ad="astra",
        space="lab",
        soft="ware",
        j="20",
        config="king",
    )
    captured = capsys.readouterr()
    assert "CRITICAL" in captured.out
    assert "THIS IS VERY CRITICAL" in captured.out
    assert '"ad": "astra"' in captured.out
    assert '"space": "lab"' in captured.out
    assert '"soft": "ware"' in captured.out
    assert '"j": "20"' in captured.out
    assert '"config": "king"' in captured.out
