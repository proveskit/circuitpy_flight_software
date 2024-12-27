Simple test
------------

Ensure your device works with this simple test.

.. literalinclude:: ../examples/mcp9808_simpletest.py
    :caption: examples/mcp9808_simpletest.py
    :linenos:


Temperature Limit test
----------------------

Show the MCP9808 to setup different temperature values

.. literalinclude:: ../examples/mcp9808_temperature_limits.py
    :caption: examples/mcp9808_temperature_limits.py
    :linenos:

MQTT with HomeAssistant
------------------------

python script to read mcp9808 temperature and publish it in mqtt.
Using discovery topic to create entity in Home Assistant.

.. literalinclude:: ../examples/mcp9808_average_temp_mqtt.py
    :caption: examples/mcp9808_average_temp_mqtt.py
    :linenos:
