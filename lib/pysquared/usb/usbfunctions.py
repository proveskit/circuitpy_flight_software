import os
import sys
import traceback

import board
import busio
import microcontroller
import sdcardio
import storage


class USBFunctions:
    def __init__(self):
        storage.remount("/", readonly=False)
        self.sd_initialized = False
        if self.init_sd():
            self.sd_initialized = True
        print("initialized USB functionalities")

    def disable_write(self):
        self.insert_data("/parameters.json", 2, '"read_state": false\n')

    def enable_write(self, reset=False):
        self.insert_data("/parameters.json", 2, '"read_state": true\n')
        if reset:
            microcontroller.reset()

    def insert_data(self, filename, line, data):
        with open(filename, "r") as f:
            lines = f.readlines()

        lines[line - 1] = data

        with open(filename, "w") as f:
            f.write("".join(map(str, lines)))

    def init_sd(self):
        spi_bus = busio.SPI(board.SPI1_SCK, board.SPI1_MOSI, board.SPI1_MISO)
        _sd = sdcardio.SDCard(spi_bus, board.SPI1_CS0, baudrate=4000000)
        _vfs = storage.VfsFat(_sd)
        storage.mount(_vfs, "/sd")
        self.fs = _vfs
        sys.path.append("/sd")
        return True

    def set_sd_file_system(self):
        self.make_file("/data/temperature.txt")

    def make_file(self, file_name, binary=False):
        try:
            ff = ""
            n = 0
            _folder = file_name[: file_name.rfind("/") + 1]
            _file = file_name[file_name.rfind("/") + 1 : file_name.rfind(".")]
            _file_type = file_name[file_name.rfind(".") + 1 :]
            print(
                "Creating new file in directory: /sd{} with file prefix: {}".format(
                    _folder, _file
                )
            )
            try:
                os.chdir("/sd" + _folder)
            except OSError:
                print("Directory {} not found. Creating...".format(_folder))
                try:
                    os.mkdir("/sd" + _folder)
                except Exception as e:
                    print(
                        "Error with creating new file: "
                        + "".join(traceback.format_exception(e))
                    )
                    return None
            for i in range(0xFFFF):
                ff = "/sd{}{}{:05}.{}".format(
                    _folder, _file, (n + i) % 0xFFFF, _file_type
                )
                try:
                    if n is not None:
                        os.stat(ff)
                except Exception:
                    n = (n + i) % 0xFFFF
                    # print('file number is',n)
                    break
            print("creating file..." + str(ff))
            if binary:
                b = "ab"
            else:
                b = "a"
            with open(ff, b) as f:
                f.tell()
            os.chdir("/")
            return ff
        except Exception as e:
            print("Error creating file: " + "".join(traceback.format_exception(e)))
            return None

    def readfile(self, path, type="string"):
        with open(path, "r") as f:
            lines = f.readlines()
        if type == "list":
            return lines
        if type == "string":
            return "".join(map(str, lines))

    def writefile(self, path, contents):
        with open(path, "w") as f:
            f.write(contents)
        return self.readfile(path)

    def appendfile(self, path, contents):
        with open(path, "a+") as f:
            f.write(contents)
        return self.readfile(path)

    def replace_line_in_file(self, path, line, contents):
        lines = self.readfile(path, "list")
        lines[line - 1] = contents
        _stringify = "".join(map(str, lines))

        return self.writefile(path, _stringify)

    def insert_line_in_file(self, path, line, contents):
        lines = self.readfile(path, type="list")
        _intermediate = lines[line - 1 :]
        lines[line:] = _intermediate
        lines[line - 1] = contents
        _stringify = "".join(map(str, lines))

        return self.writefile(path, _stringify)

    def copyfile(self, to_path, from_path):
        # TODO: Make file if not exist. look into why from_path file get rewritten. bug?
        contents = self.readfile(from_path)
        return self.writefile(to_path, contents)

    def print_directory(self, path, tabs=0):
        for file in os.listdir(path):
            if file == "?":
                continue  # Issue noted in Learn
            stats = os.stat(path + "/" + file)
            filesize = stats[6]
            isdir = stats[0] & 0x4000

            if filesize < 1000:
                sizestr = str(filesize) + " by"
            elif filesize < 1000000:
                sizestr = "%0.1f KB" % (filesize / 1000)
            else:
                sizestr = "%0.1f MB" % (filesize / 1000000)

            prettyprintname = ""
            for _ in range(tabs):
                prettyprintname += "   "
            prettyprintname += file
            if isdir:
                prettyprintname += "/"
            print("{0:<40} Size: {1:>10}".format(prettyprintname, sizestr))

            # recursively print directory contents
            if isdir:
                self.print_directory(path + "/" + file, tabs + 1)

    def delete_file(self, path):
        os.remove(path)

    def delete_directory(self, path, recursive=False):
        # TODO: add recursive functionality to remove files
        # logic to check if directory is not empty. If it is delete regardless of recursion, if it is not check for if recursion is enabled
        if path == "/sd":
            print("you really shouldnt try to delete your root directory")
        else:
            os.chdir("/sd")
            os.rmdir(path)
