.PHONY: fmt
fmt:
	pre-commit run --all-files

.PHONY: test
test:
	python3 -m pytest tests/unit

download-libraries: \
	adafruit-drv2605 \
	adafruit-lis2mdl \
	adafruit-lsm303-accel \
	adafruit-lsm6ds \
	adafruit-mcp2515 \
	adafruit-mcp9808 \
	adafruit-neopixel \
	adafruit-ov5640 \
	adafruit-pca9685 \
	adafruit-register \
	adafruit-rfm \
	adafruit-tca9548a \
	adafruit-ticks \
	adafruit-veml7700

LIBDIR ?= proves/lib
$(LIBDIR):
	mkdir -p $(LIBDIR)

# Library Versions
ADAFRUIT_ASYNCIO_VERSION ?= 1.3.3
ADAFRUIT_DRV2605_VERSION ?= 1.3.4
ADAFRUIT_LIS2MDL_VERSION ?= 2.1.23
ADAFRUIT_LSM303_ACCEL_VERSION ?= 1.1.22
ADAFRUIT_LSM6DS_VERSION ?= 4.5.13
ADAFRUIT_MCP2515_VERSION ?= 1.1.6
ADAFRUIT_MCP9808_VERSION ?= 3.3.24
ADAFRUIT_NEOPIXEL_VERSION ?= 6.3.12
ADAFRUIT_OV5640_VERSION ?= 1.2.1
ADAFRUIT_PCA9685_VERSION ?= 3.4.16
ADAFRUIT_REGISTER_VERSION ?= 1.10.1
ADAFRUIT_RFM_VERSION ?= 1.0.3
ADAFRUIT_TCA9548A_VERSION ?= 0.7.4
ADAFRUIT_TICKS_VERSION ?= 1.1.1
ADAFRUIT_VEML7700_VERSION ?= 2.0.2

.PHONY: adafruit-asyncio
adafruit-asyncio: $(LIBDIR)
	pip install git+https://github.com/adafruit/adafruit_circuitpython_asyncio@$(ADAFRUIT_ASYNCIO_VERSION) --target $(LIBDIR) --no-deps
	rm -rf $(LIBDIR)/adafruit_circuitpython_asyncio-0.0.0+auto.0.dist-info

.PHONY: adafruit-drv2605
adafruit-drv2605: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-drv2605,$(ADAFRUIT_DRV2605_VERSION),$(LIBDIR))

.PHONY: adafruit-lis2mdl
adafruit-lis2mdl: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-lis2mdl,$(ADAFRUIT_LIS2MDL_VERSION),$(LIBDIR))

.PHONY: adafruit-lsm303-accel
adafruit-lsm303-accel: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-lsm303_accel,$(ADAFRUIT_LSM303_ACCEL_VERSION),$(LIBDIR))

.PHONY: adafruit-lsm6ds
adafruit-lsm6ds: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-lsm6ds,$(ADAFRUIT_LSM6DS_VERSION),$(LIBDIR))

.PHONY: adafruit-mcp2515
adafruit-mcp2515: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-mcp2515,$(ADAFRUIT_MCP2515_VERSION),$(LIBDIR))

.PHONY: adafruit-mcp9808
adafruit-mcp9808: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-mcp9808,$(ADAFRUIT_MCP9808_VERSION),$(LIBDIR))

.PHONY: adafruit-neopixel
adafruit-neopixel: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-neopixel,$(ADAFRUIT_NEOPIXEL_VERSION),$(LIBDIR))

.PHONY: adafruit-ov5640
adafruit-ov5640: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-ov5640,$(ADAFRUIT_OV5640_VERSION),$(LIBDIR))

.PHONY: adafruit-pca9685
adafruit-pca9685: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-pca9685,$(ADAFRUIT_PCA9685_VERSION),$(LIBDIR))

.PHONY: adafruit-register
adafruit-register: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-register,$(ADAFRUIT_REGISTER_VERSION),$(LIBDIR))

.PHONY: adafruit-rfm
adafruit-rfm: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-rfm,$(ADAFRUIT_RFM_VERSION),$(LIBDIR))

.PHONY: adafruit-ticks
adafruit-ticks: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-ticks,$(ADAFRUIT_TICKS_VERSION),$(LIBDIR))

.PHONY: adafruit-tca9548a
adafruit-tca9548a: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-tca9548a,$(ADAFRUIT_TCA9548A_VERSION),$(LIBDIR))

.PHONY: adafruit-veml7700
adafruit-veml7700: $(LIBDIR)
	$(call install_lib,adafruit-circuitpython-veml7700,$(ADAFRUIT_VEML7700_VERSION),$(LIBDIR))

define install_lib
	pip install $(1)==$(2) --target $(3) --no-deps
	rm -rf $(3)/$(subst -,_,$(1))-$(2).dist-info
endef
