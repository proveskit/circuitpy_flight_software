Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-ov5640/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/ov5640/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_ov5640/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_ov5640/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

CircuitPython driver for OV5640 Camera


Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_ov5640

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block: python

    """Capture an image from the camera and display it as ASCII art.

    This demo is designed to run on the Kaluga, but you can adapt it
    to other boards by changing the constructors for `bus` and `cam`
    appropriately.

    The camera is placed in YUV mode, so the top 8 bits of each color
    value can be treated as "greyscale".

    It's important that you use a terminal program that can interpret
    "ANSI" escape sequences.  The demo uses them to "paint" each frame
    on top of the prevous one, rather than scrolling.

    Remember to take the lens cap off, or un-comment the line setting
    the test pattern!
    """

    import sys
    import time

    import busio
    import board

    import adafruit_ov5640

    print("construct bus")
    bus = busio.I2C(scl=board.CAMERA_SIOC, sda=board.CAMERA_SIOD)
    print("construct camera")
    cam = adafruit_ov5640.OV5640(
        bus,
        data_pins=board.CAMERA_DATA,
        clock=board.CAMERA_PCLK,
        vsync=board.CAMERA_VSYNC,
        href=board.CAMERA_HREF,
        mclk=board.CAMERA_XCLK,
        size=adafruit_ov5640.OV5640_SIZE_QQVGA,
    )
    print("print chip id")
    print(cam.chip_id)


    cam.colorspace = adafruit_ov5640.OV5640_COLOR_YUV
    cam.flip_y = True
    cam.flip_x = True
    cam.test_pattern = False

    buf = bytearray(cam.capture_buffer_size)
    chars = b" .':-+=*%$#"
    remap = [chars[i * (len(chars) - 1) // 255] for i in range(256)]

    width = cam.width
    row = bytearray(width)

    print("capturing")
    cam.capture(buf)
    print("capture complete")

    sys.stdout.write("\033[2J")
    while True:
        cam.capture(buf)
        for j in range(0, cam.height, 2):
            sys.stdout.write(f"\033[{j//2}H")
            for i in range(cam.width):
                row[i] = remap[buf[2 * (width * j + i)]]
            sys.stdout.write(row)
            sys.stdout.write("\033[K")
        sys.stdout.write("\033[J")
        time.sleep(0.05)

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/ov5640/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_ov5640/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
