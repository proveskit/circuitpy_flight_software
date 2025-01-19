# Development Guide for Linux

## Setup

To set up your development environment on Linux, follow these steps:

1. Update your package list and install the necessary packages:
    ```sh
    sudo apt update && sudo apt install make python3.12-venv zip
    ```

You should now be able to run the `make` command in the root of the repo to get started.

### A note on `make install`
`make install` is a command that can be used to quickly install the code you're working on onto the board. On linux you can use the `findmnt` command to locate your board's mount point.
```sh
findmnt
...
├─/media/username/SOME-VALUE /dev/sdb1 vfat rw,nosuid,nodev,relatime 0 0
```

For example, if the board is mounted at `/media/username/SOME-VALUE` then your install command will look like:
```sh
make install BOARD_MOUNT_POINT=/media/username/SOME-VALUE/
```
