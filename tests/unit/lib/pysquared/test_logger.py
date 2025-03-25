import pytest

import lib.pysquared.nvm.counter as counter
from lib.pysquared.logger import Logger, _color
from mocks.circuitpython.byte_array import ByteArray


@pytest.fixture
def logger():
    datastore = ByteArray(size=8)
    index = 0
    count = counter.Counter(index, datastore)
    return Logger(count)


@pytest.fixture
def logger_color():
    datastore = ByteArray(size=8)
    index = 0
    count = counter.Counter(index, datastore)
    return Logger(error_counter=count, colorized=True)


def test_debug_log(capsys, logger):
    logger.debug("This is a debug message", blake="jameson")
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "This is a debug message" in captured.out
    assert '"blake": "jameson"' in captured.out


def test_debug_with_err(capsys, logger):
    logger.debug(
        "This is another debug message", err=OSError("Manually creating an OS Error")
    )
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "This is another debug message" in captured.out
    assert "OSError: Manually creating an OS Error" in captured.out


def test_info_log(capsys, logger):
    logger.info(
        "This is a info message!!",
        foo="bar",
    )
    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "This is a info message!!" in captured.out
    assert '"foo": "bar"' in captured.out


def test_info_with_err(capsys, logger):
    logger.info(
        "This is a info message!!",
        foo="barrrr",
        err=OSError("Manually creating an OS Error"),
    )
    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "This is a info message!!" in captured.out
    assert '"foo": "barrrr"' in captured.out
    assert "OSError: Manually creating an OS Error" in captured.out


def test_warning_log(capsys, logger):
    logger.warning(
        "This is a warning message!!??!",
        boo="bar",
        pleiades="maia",
        cube="sat",
        err=Exception("manual exception"),
    )
    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "This is a warning message!!??!" in captured.out
    assert '"boo": "bar"' in captured.out
    assert '"pleiades": "maia"' in captured.out
    assert '"cube": "sat"' in captured.out
    assert "Exception: manual exception" in captured.out


def test_error_log(capsys, logger):
    logger.error(
        "This is an error message",
        OSError("Manually creating an OS Error for testing"),
        hee="haa",
        pleiades="five",
        please="work",
    )
    captured = capsys.readouterr()
    assert "ERROR" in captured.out
    assert "This is an error message" in captured.out
    assert '"hee": "haa"' in captured.out
    assert '"pleiades": "five"' in captured.out
    assert '"please": "work"' in captured.out
    assert "OSError: Manually creating an OS Error for testing" in captured.out


def test_critical_log(capsys, logger):
    logger.critical(
        "THIS IS VERY CRITICAL",
        OSError("Manually creating an OS Error"),
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


def test_type_error_log(capsys, logger):
    logger.info("Testing type error", bad_arg=lambda x: x + 1)
    captured = capsys.readouterr()
    assert '"level": "ERROR"' in captured.out
    assert "Failed to serialize log message:" in captured.out
    assert "Object of type function is not JSON serializable" in captured.out


def test_debug_log_color(capsys, logger_color):
    logger_color.debug("This is a debug message", blake="jameson")
    captured = capsys.readouterr()
    assert _color(msg="DEBUG", color="blue") in captured.out
    assert "This is a debug message" in captured.out
    assert '"blake": "jameson"' in captured.out


def test_info_log_color(capsys, logger_color):
    logger_color.info("This is a info message!!", foo="bar")
    captured = capsys.readouterr()
    assert _color(msg="INFO", color="green") in captured.out
    assert "This is a info message!!" in captured.out
    assert '"foo": "bar"' in captured.out


def test_warning_log_color(capsys, logger_color):
    logger_color.warning(
        "This is a warning message!!??!", boo="bar", pleiades="maia", cube="sat"
    )
    captured = capsys.readouterr()
    assert _color(msg="WARNING", color="orange") in captured.out
    assert "This is a warning message!!??!" in captured.out
    assert '"boo": "bar"' in captured.out
    assert '"pleiades": "maia"' in captured.out
    assert '"cube": "sat"' in captured.out


def test_error_log_color(capsys, logger_color):
    logger_color.error(
        "This is an error message",
        hee="haa",
        pleiades="five",
        please="work",
        err=OSError("Manually creating an OS Error"),
    )
    captured = capsys.readouterr()
    assert _color(msg="ERROR", color="pink") in captured.out
    assert "This is an error message" in captured.out
    assert '"hee": "haa"' in captured.out
    assert '"pleiades": "five"' in captured.out
    assert '"please": "work"' in captured.out


def test_critical_log_color(capsys, logger_color):
    logger_color.critical(
        "THIS IS VERY CRITICAL",
        ad="astra",
        space="lab",
        soft="ware",
        j="20",
        config="king",
        err=OSError("Manually creating an OS Error"),
    )
    captured = capsys.readouterr()
    assert _color(msg="CRITICAL", color="red") in captured.out
    assert "THIS IS VERY CRITICAL" in captured.out
    assert '"ad": "astra"' in captured.out
    assert '"space": "lab"' in captured.out
    assert '"soft": "ware"' in captured.out
    assert '"j": "20"' in captured.out
    assert '"config": "king"' in captured.out
