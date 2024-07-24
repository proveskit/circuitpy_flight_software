import time
import random

# our 4 byte code to authorize commands
# pass-code for DEMO PURPOSES ONLY
jokereply = [
    "Your Mom",
    "Your Mum",
    "Your Face",
    "not True lol",
    "I have brought peace, freedom, justice, and security to my new empire! Your New Empire?",
]
# our 4 byte code to authorize commands
# pass-code for DEMO PURPOSES ONLY
super_secret_code = b""  # put your own code here
print(f"Super secret code is: {super_secret_code}")
commands = {
    b"\x8eb": "noop",
    b"\xd4\x9f": "hreset",  # new
    b"\x12\x06": "shutdown",
    b"8\x93": "query",  # new
    b"\x96\xa2": "exec_cmd",
    b"\xa5\xb4": "joke_reply",
    b"\x56\xc4": "FSK",
}


############### hot start helper ###############
def hotstart_handler(cubesat, msg):
    # try
    try:
        cubesat.radio1.node = cubesat.cfg["id"]  # this sat's radiohead ID
        cubesat.radio1.destination = cubesat.cfg["gs"]  # target gs radiohead ID
    except:
        pass
    # check that message is for me
    if msg[0] == cubesat.radio1.node:
        # TODO check for optional radio config

        # manually send ACK
        cubesat.radio1.send("!", identifier=msg[2], flags=0x80)
        # TODO remove this delay. for testing only!
        time.sleep(0.5)
        message_handler(cubesat, msg)
    else:
        print(
            f"not for me? target id: {hex(msg[0])}, my id: {hex(cubesat.radio1.node)}"
        )


############### message handler ###############
def message_handler(cubesat, msg):
    multi_msg = False
    if len(msg) >= 10:  # [RH header 4 bytes] [pass-code(4 bytes)] [cmd 2 bytes]
        if bytes(msg[4:8]) == super_secret_code:
            # check if multi-message flag is set
            if msg[3] & 0x08:
                multi_msg = True
            # strip off RH header
            msg = bytes(msg[4:])
            cmd = msg[4:6]  # [pass-code(4 bytes)] [cmd 2 bytes] [args]
            cmd_args = None
            if len(msg) > 6:
                print("command with args")
                try:
                    cmd_args = msg[6:]  # arguments are everything after
                    print("cmd args: {}".format(cmd_args))
                except Exception as e:
                    print("arg decoding error: {}".format(e))
            if cmd in commands:
                try:
                    if cmd_args is None:
                        print("running {} (no args)".format(commands[cmd]))
                        # eval a string turns it into a func name
                        eval(commands[cmd])(cubesat)
                    else:
                        print(
                            "running {} (with args: {})".format(commands[cmd], cmd_args)
                        )
                        eval(commands[cmd])(cubesat, cmd_args)
                except Exception as e:
                    print("something went wrong: {}".format(e))
                    cubesat.radio1.send(str(e).encode())
            else:
                print("invalid command!")
                cubesat.radio1.send(b"invalid cmd" + msg[4:])
            # check for multi-message mode
            if multi_msg:
                # TODO check for optional radio config
                print("multi-message mode enabled")
                response = cubesat.radio1.receive(
                    keep_listening=True,
                    with_ack=True,
                    with_header=True,
                    view=True,
                    timeout=10,
                )
                if response is not None:
                    cubesat.c_gs_resp += 1
                    message_handler(cubesat, response)
        else:
            print("bad code?")


########### commands without arguments ###########
def noop(cubesat):
    print("no-op")
    pass


def hreset(cubesat):
    print("Resetting")
    try:
        cubesat.radio1.send(data=b"resetting")
        cubesat.micro.on_next_reset(self.cubesat.micro.RunMode.NORMAL)
        cubesat.micro.reset()
    except:
        pass


def FSK(cubesat):
    cubesat.f_fsk = True


def joke_reply(cubesat):
    joke = random.choice(jokereply)
    print(joke)
    cubesat.radio1.send(joke)


########### commands with arguments ###########


def shutdown(cubesat, args):
    # make shutdown require yet another pass-code
    if args == b"\x0b\xfdI\xec":
        print("valid shutdown command received")
        # set shutdown NVM bit flag
        cubesat.f_shtdwn = True

        """
        Exercise for the user:
            Implement a means of waking up from shutdown
            See beep-sat guide for more details
            https://pycubed.org/resources
        """

        # deep sleep + listen
        # TODO config radio
        cubesat.radio1.listen()
        if "st" in cubesat.radio_cfg:
            _t = cubesat.radio_cfg["st"]
        else:
            _t = 5
        import alarm

        time_alarm = alarm.time.TimeAlarm(
            monotonic_time=time.monotonic() + eval("1e" + str(_t))
        )  # default 1 day
        # set hot start flag right before sleeping
        cubesat.f_hotstrt = True
        alarm.exit_and_deep_sleep_until_alarms(time_alarm)


def query(cubesat, args):
    print(f"query: {args}")
    print(cubesat.radio1.send(data=str(eval(args))))


def exec_cmd(cubesat, args):
    print(f"exec: {args}")
    exec(args)
