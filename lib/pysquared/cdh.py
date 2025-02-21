import random
import time

import alarm

from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite

try:
    from typing import Any, Union

    import circuitpython_typing
except Exception:
    pass


class CommandDataHandler:
    """
    Constructor
    """

    def __init__(self, config: Config, logger: Logger) -> None:
        self.logger: Logger = logger
        self._commands: dict[bytes, str] = {
            b"\x8eb": "noop",
            b"\xd4\x9f": "hreset",
            b"\x12\x06": "shutdown",
            b"8\x93": "query",
            b"\x96\xa2": "exec_cmd",
            b"\xa5\xb4": "joke_reply",
            b"\x56\xc4": "FSK",
        }
        self._joke_reply: list[str] = config.joke_reply
        self._super_secret_code: bytes = config.super_secret_code.encode("utf-8")
        self._repeat_code: bytes = config.repeat_code.encode("utf-8")
        self.logger.info(
            "The satellite has a super secret code!",
            super_secret_code=self._super_secret_code,
        )

    ############### hot start helper ###############
    def hotstart_handler(self, cubesat: Satellite, msg: Any) -> None:
        # check that message is for me
        if msg[0] == cubesat.radio1.node:
            # TODO check for optional radio config

            # manually send ACK
            cubesat.radio1.send("!", identifier=msg[2], flags=0x80)
            # TODO remove this delay. for testing only!
            time.sleep(0.5)
            self.message_handler(cubesat, msg)
        else:
            self.logger.info(
                "Message not for me?",
                target_id=hex(msg[0]),
                my_id=hex(cubesat.radio1.node),
            )

    ############### message handler ###############
    def parse_message(self, msg: bytearray) -> tuple[bool, bytes, Union[bytes, None]]:
        # check if multi-message flag is set
        if msg[3] & 0x08:
            multi_msg = True
        # strip off RH header
        received_msg: bytes = bytes(msg[4:])
        cmd: bytes = received_msg[4:6]  # [pass-code(4 bytes)] [cmd 2 bytes] [args]
        cmd_args: Union[bytes, None] = None
        if len(received_msg) > 6:
            self.logger.info("This is a command with args")
        try:
            cmd_args = received_msg[6:]  # arguments are everything after
            self.logger.info("Here are the command arguments", cmd_args=cmd_args)
        except Exception as e:
            self.logger.error("There was an error decoding the arguments", e)

        return multi_msg, cmd, cmd_args

    def handle_command(
        self,
        cubesat: Satellite,
        msg: bytearray,
        multi_msg: bool,
        cmd: bytes,
        cmd_args: Union[bytes, None],
    ) -> None:
        if cmd not in self._commands:
            self.logger.info("invalid command!")
            cubesat.radio1.send(b"invalid cmd" + msg[4:])
            # check for multi-message mode
            if multi_msg:
                # TODO check for optional radio config
                self.logger.info("multi-message mode enabled")

            response: bytearray = cubesat.radio1.receive(
                keep_listening=True,
                with_ack=True,
                with_header=True,
                view=True,
                timeout=10,
            )

            if response is not None:
                self.message_handler(cubesat, response)
            return

        try:
            if cmd_args is None:
                self.logger.info(
                    "There are no args provided", command=self._commands[cmd]
                )
                # eval a string turns it into a func name
                eval(self._commands[cmd])(cubesat)
            else:
                self.logger.info(
                    "running command with args",
                    command=self._commands[cmd],
                    cmd_args=cmd_args,
                )
                eval(self._commands[cmd])(cubesat, cmd_args)
        except Exception as e:
            self.logger.error("something went wrong!", e)
            cubesat.radio1.send(str(e).encode())

    def message_handler(self, cubesat: Satellite, msg: bytearray) -> None:
        multi_msg: bool = False

        if not (len(msg) >= 10 or bytes(msg[4:6]) == self._repeat_code):
            self.logger.info("bad code?")
            return

        if bytes(msg[4:6]) == self._repeat_code:
            self.logger.info("Repeating last message!")
            try:
                cubesat.radio1.send(msg[6:])
            except Exception as e:
                self.logger.error("There was an error repeating the message!", e)
            return

        if bytes(msg[4:8]) == self._super_secret_code:
            multi_msg, cmd, cmd_args = self.parse_message(msg)

        self.handle_command(cubesat, msg, multi_msg, cmd, cmd_args)

    ########### commands without arguments ###########
    def noop(self) -> None:
        self.logger.info("no-op")

    def hreset(self, cubesat: Satellite) -> None:
        self.logger.info("Resetting")
        try:
            cubesat.radio1.send(data=b"resetting")
            cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)  # type: ignore
            cubesat.micro.reset()  # type: ignore
        except Exception:
            pass

    @staticmethod
    def toggle_fsk_signal(cubesat: Satellite) -> None:
        cubesat.f_fsk.toggle(True)

    def joke_reply(self, cubesat: Satellite) -> None:
        joke: str = random.choice(self._joke_reply)
        self.logger.info("Sending joke reply", joke=joke)
        cubesat.radio1.send(joke)

    ########### commands with arguments ###########

    def shutdown(self, cubesat: Satellite, args: bytes) -> None:
        # make shutdown require yet another pass-code
        if args != b"\x0b\xfdI\xec":
            return

        # This means args does = b"\x0b\xfdI\xec"
        self.logger.info("valid shutdown command received")
        # set shutdown NVM bit flag
        cubesat.f_shtdwn.toggle(True)

        """
        Exercise for the user:
            Implement a means of waking up from shutdown
            See beep-sat guide for more details
            https://pycubed.org/resources
        """

        # deep sleep + listen
        # TODO config radio
        cubesat.radio1.listen()
        _t: float

        if cubesat.config.radio_cfg.start_time is not None:
            _t = cubesat.config.radio_cfg.start_time
        else:
            _t = 5

        time_alarm: circuitpython_typing.Alarm = alarm.time.TimeAlarm(
            monotonic_time=time.monotonic() + 10**_t
        )  # default 1 day
        alarm.exit_and_deep_sleep_until_alarms(time_alarm)

    def query(self, cubesat: Satellite, args: str) -> None:
        self.logger.info("Sending query with args", args=args)

        cubesat.radio1.send(data=str(eval(args)))

    def exec_cmd(self, args: str) -> None:
        self.logger.info("Executing command", args=args)
        exec(args)
