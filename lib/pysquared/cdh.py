import random
import time

from lib.adafruit_rfm.rfm_common import RFMSPI
from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite


class CommandDataHandler:
    """
    Constructor
    """

    def __init__(self, config: Config, logger: Logger, radio: RFMSPI) -> None:
        self.logger = logger
        self._commands: dict = {
            b"\x8eb": "noop",
            b"\xd4\x9f": "hreset",
            b"\x12\x06": "shutdown",
            b"8\x93": "query",
            b"\x96\xa2": "exec_cmd",
            b"\xa5\xb4": "joke_reply",
            b"\x56\xc4": "FSK",
        }
        self._jokereply: list[str] = config.get_list("jokereply")
        self._super_secret_code: str = config.get_str("super_secret_code").encode(
            "utf-8"
        )
        self._repeat_code: str = config.get_str("repeat_code").encode("utf-8")
        self.radio = radio

        self.logger.info(
            "The satellite has a super secret code!",
            super_secret_code=self._super_secret_code,
        )

    ############### hot start helper ###############
    def hotstart_handler(self, cubesat: Satellite, msg) -> None:
        # check that message is for me
        if msg[0] == self.radio.node:
            # TODO check for optional radio config

            # manually send ACK
            self.radio.send("!", identifier=msg[2], flags=0x80)
            # TODO remove this delay. for testing only!
            time.sleep(0.5)
            self.message_handler(cubesat, msg)
        else:
            self.logger.info(
                "Message not for me?",
                target_id=hex(msg[0]),
                my_id=hex(self.radio.node),
            )

    ############### message handler ###############
    def message_handler(self, cubesat: Satellite, msg) -> None:
        multi_msg: bool = False
        if len(msg) >= 10:  # [RH header 4 bytes] [pass-code(4 bytes)] [cmd 2 bytes]
            if bytes(msg[4:8]) == self._super_secret_code:
                # check if multi-message flag is set
                if msg[3] & 0x08:
                    multi_msg = True
                # strip off RH header
                msg = bytes(msg[4:])
                cmd = msg[4:6]  # [pass-code(4 bytes)] [cmd 2 bytes] [args]
                cmd_args = None
                if len(msg) > 6:
                    self.logger.info("This is a command with args")
                try:
                    cmd_args = msg[6:]  # arguments are everything after
                    self.logger.info(
                        "Here are the command arguments", cmd_args=cmd_args
                    )
                except Exception as e:
                    self.logger.error(
                        "There was an error decoding the arguments", err=e
                    )
            if cmd in self._commands:
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
                    self.logger.error("something went wrong!", err=e)
                    self.radio.send(str(e).encode())
            else:
                self.logger.info("invalid command!")
                self.radio.send(b"invalid cmd" + msg[4:])
                # check for multi-message mode
                if multi_msg:
                    # TODO check for optional radio config
                    self.logger.info("multi-message mode enabled")
                response = self.radio.receive(
                    keep_listening=True,
                    with_ack=True,
                    with_header=True,
                    view=True,
                    timeout=10,
                )
                if response is not None:
                    cubesat.c_gs_resp += 1
                    self.message_handler(cubesat, response)
        elif bytes(msg[4:6]) == self._repeat_code:
            self.logger.info("Repeating last message!")
            try:
                self.radio.send(msg[6:])
            except Exception as e:
                self.logger.error("There was an error repeating the message!", err=e)
        else:
            self.logger.info("bad code?")

    ########### commands without arguments ###########
    def noop(self) -> None:
        self.logger.info("no-op")

    def hreset(self, cubesat: Satellite) -> None:
        self.logger.info("Resetting")
        try:
            self.radio.send(data=b"resetting")
            cubesat.micro.on_next_reset(cubesat.micro.RunMode.NORMAL)
            cubesat.micro.reset()
        except Exception:
            pass

    def FSK(cubesat: Satellite) -> None:
        cubesat.f_fsk.toggle(True)

    def joke_reply(self, cubesat: Satellite) -> None:
        joke: str = random.choice(self._jokereply)
        self.logger.info("Sending joke reply", joke=joke)
        self.radio.send(joke)

    ########### commands with arguments ###########

    def shutdown(self, cubesat: Satellite, args) -> None:
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
        self.radio.listen()
        if "st" in cubesat.radio_cfg:
            _t = cubesat.radio_cfg["st"]
        else:
            _t = 5
        import alarm

        time_alarm = alarm.time.TimeAlarm(
            monotonic_time=time.monotonic() + eval("1e" + str(_t))
        )  # default 1 day
        # set hot start flag right before sleeping
        cubesat.f_hotstrt.toggle(True)
        alarm.exit_and_deep_sleep_until_alarms(time_alarm)

    def query(self, cubesat: Satellite, args) -> None:
        self.logger.info("Sending query with args", args=args)

        self.radio.send(data=str(eval(args)))

    def exec_cmd(self, cubesat: Satellite, args) -> None:
        self.logger.info("Executing command", args=args)
        exec(args)
