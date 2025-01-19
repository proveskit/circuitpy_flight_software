# Development Guide for MacOS

## Setup

To get started with development on MacOS, follow these steps:

1. **Install Xcode Command Line Tools**: These tools are necessary for compiling and building software.
    ```sh
    xcode-select --install
    ```

You should now be able to run the `make` command in the root of the repo to get started.

### A note on `make install`
`make install` is a command that can be used to quickly install the code you're working on onto the board. On Mac, you can find the location of your mount by looking for a mount named `PYSQUARED` in your `/Volumes` directory
```sh
ls -lah /Volumes | grep PYSQUARED
...
drwx------@  1 nate  staff    16K Jan  9 08:09 PYSQUARED/
```

For example, if the board is mounted at `/Volumes/PYSQUARED/` then your install command will look like:
```sh
make install BOARD_MOUNT_POINT=/Volumes/PYSQUARED/
```
