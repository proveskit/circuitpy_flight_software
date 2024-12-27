Simple test
------------

Ensure your device works with this simple test.

.. literalinclude:: ../examples/ov5640_simpletest.py
    :caption: examples/ov5640_simpletest.py
    :linenos:

Directio
--------
Use an LCD as a viewfinder, bypassing displayio

.. literalinclude:: ../examples/ov5640_directio_kaluga1_3_ili9341.py
    :caption: examples/ov5640_directio_kaluga1_3_ili9341.py
    :linenos:

JPEG (internal storage)
-----------------------
Record JPEG images onto internal storage.  Requires use of ov5640_jpeg_kaluga1_3_boot.py (below) as boot.py.

.. literalinclude:: ../examples/ov5640_jpeg_kaluga1_3.py
    :caption: examples/ov5640_jpeg_kaluga1_3.py
    :linenos:

Use with above example as boot.py

.. literalinclude:: ../examples/ov5640_jpeg_kaluga1_3_boot.py
    :caption: examples/ov5640_jpeg_kaluga1_3_boot.py
    :linenos:

JPEG (SD card)
--------------
Record JPEG images to an SD card.

.. literalinclude:: ../examples/ov5640_sdcard_kaluga_1_3.py
    :caption: examples/ov5640_sdcard_kaluga_1_3.py
    :linenos:

GIF (SD card)
-------------

Record stop-motion GIF images to an SD card.

.. literalinclude:: ../examples/ov5640_stopmotion_kaluga1_3.py
    :caption: examples/ov5640_stopmotion_kaluga1_3.py
    :linenos:
