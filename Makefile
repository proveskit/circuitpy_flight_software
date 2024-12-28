.PHONY: fmt
fmt:
	pre-commit run --all-files

.PHONY: test
test:
	pytest FC_Board/tests

.PHONY: build
build:
	echo "pass"

FC_Board/lib:
	mkdir -p FC_Board/lib

# FC_Board/lib/adafruit_drv2605.mpy: FC_Board/lib
# 	venv/bin/mpy-cross -o FC_Board/lib/adafruit_drv2605.mpy lib/adafruit_drv2605/adafruit_drv2605.py

# FC_Board/lib/adafruit_lis2mdl.mpy: FC_Board/lib
# 	venv/bin/mpy-cross -o FC_Board/lib/adafruit_lis2mdl.mpy lib/adafruit_lis2mdl/adafruit_lis2mdl.py

# FC_Board/lib/adafruit_lsm6ds.mpy: FC_Board/lib
# 	venv/bin/mpy-cross -o FC_Board/lib/adafruit_lsm6ds.mpy lib/adafruit_lsm6ds/adafruit_lsm6ds

# FC_Board/lib/adafruit_lsm303_accel.mpy: FC_Board/lib
# 	venv/bin/mpy-cross -o FC_Board/lib/adafruit_lsm303_accel.mpy lib/adafruit_lsm303_accel/adafruit_lsm303_accel.py

# FC_Board/lib/adafruit_mcp2515.mpy: FC_Board/lib
# 	venv/bin/mpy-cross -o FC_Board/lib/adafruit_mcp2515.mpy lib/adafruit_mcp2515/adafruit_mcp2515.py

# FC_Board/lib/adafruit_mcp9808.mpy: FC_Board/lib
# 	venv/bin/mpy-cross -o FC_Board/lib/adafruit_mcp9808.mpy lib/adafruit_mcp9808/adafruit_mcp9808.py

FC_Board/proveskit_functions.mpy:
	venv/bin/mpy-cross -o FC_Board/proveskit_functions.mpy lib/proveskit_functions/functions.py
