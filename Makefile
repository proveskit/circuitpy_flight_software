.PHONY: fmt
fmt:
	pre-commit run --all-files

.PHONY: test
test:
	pytest src/tests

.PHONY: build
build: artifacts/lib artifacts/lib/proveskit_functions.mpy
	@rsync -av --exclude='lib' --exclude='tests' src/ artifacts/ > /dev/null

# Define a list of libraries to be copied
LIBRARIES = \
	adafruit_drv2605/adafruit_drv2605.py \
	adafruit_lis2mdl/adafruit_lis2mdl.py \
	adafruit_lsm6ds/adafruit_lsm6ds \
	adafruit_lsm303_accel/adafruit_lsm303_accel.py \
	adafruit_mcp2515/adafruit_mcp2515 \
	adafruit_mcp9808/adafruit_mcp9808.py \
	adafruit_neopixel/neopixel.py \
	adafruit_ov5640/adafruit_ov5640 \
	adafruit_pca9685/adafruit_pca9685.py \
	adafruit_register/adafruit_register \
	adafruit_rfm/adafruit_rfm \
	adafruit_tca9548a/adafruit_tca9548a.py \
	adafruit_ticks/adafruit_ticks.py \
	adafruit_velm7700/adafruit_velm7700.py \
	proveskit_functions

# Rule to copy each library
define copy_rule
artifacts/lib/$(1): artifacts/lib
	mkdir -p $$(dirname artifacts/lib/$(1))
	cp -r src/lib/$(1) artifacts/lib/$(1)
endef

# Generate the copy rules for each library
$(foreach lib, $(LIBRARIES), $(eval $(call copy_rule, $(lib))))
