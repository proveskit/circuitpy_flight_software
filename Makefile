.PHONY: all
all: download-libraries help

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: fmt
fmt: ## Lint and format files
	pre-commit run --all-files

.PHONY: test
test: ## Run tests
	python3 -m pytest tests/unit

##@ Build

.PHONY: build
build: download-libraries ## Build the project, store the result in the artifacts directory
	mkdir -p artifacts/proves
	cp ./*.py artifacts/proves/
	find ./lib -type d -name '__pycache__' -prune -o -type f -print | cpio -pdm artifacts/proves/
	cd artifacts && zip -r proves.zip proves

##@ Library Management

.PHONY: download-libraries
download-libraries: \
	adafruit-asyncio \
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

LIBDIR ?= lib
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

ADAFRUIT_ASYNCIO ?= lib/asyncio
.PHONY: adafruit-asyncio
adafruit-asyncio: $(ADAFRUIT_ASYNCIO) ## Download the adafruit-circuitpython-asyncio library
$(ADAFRUIT_ASYNCIO): $(LIBDIR)
	@test -s $(ADAFRUIT_ASYNCIO) || { \
		pip install git+https://github.com/adafruit/adafruit_circuitpython_asyncio@$(ADAFRUIT_ASYNCIO_VERSION) --target $(LIBDIR) --no-deps; \
		rm -rf $(LIBDIR)/adafruit_circuitpython_asyncio-0.0.0+auto.0.dist-info; \
	}

ADAFRUIT_DRV2605 ?= lib/adafruit_drv2605.py
.PHONY: adafruit-drv2605
adafruit-drv2605: $(ADAFRUIT_DRV2605) ## Download the adafruit-circuitpython-drv2605 library
$(ADAFRUIT_DRV2605): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_DRV2605),adafruit-circuitpython-drv2605,$(ADAFRUIT_DRV2605_VERSION),$(LIBDIR))

ADAFRUIT_LIS2MDL ?= lib/adafruit_lis2mdl.py
.PHONY: adafruit-lis2mdl
adafruit-lis2mdl: $(ADAFRUIT_LIS2MDL) ## Download the adafruit-circuitpython-lis2mdl library
$(ADAFRUIT_LIS2MDL): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_LIS2MDL),adafruit-circuitpython-lis2mdl,$(ADAFRUIT_LIS2MDL_VERSION),$(LIBDIR))

ADAFRUIT_LSM303_ACCEL ?= lib/adafruit_lsm303_accel.py
.PHONY: adafruit-lsm303-accel
adafruit-lsm303-accel: $(ADAFRUIT_LSM303_ACCEL) ## Download the adafruit-circuitpython-lsm303-accel library
$(ADAFRUIT_LSM303_ACCEL): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_LSM303_ACCEL),adafruit-circuitpython-lsm303-accel,$(ADAFRUIT_LSM303_ACCEL_VERSION),$(LIBDIR))

ADAFRUIT_LSM6DS ?= lib/adafruit_lsm6ds
.PHONY: adafruit-lsm6ds
adafruit-lsm6ds: $(ADAFRUIT_LSM6DS) ## Download the adafruit-circuitpython-lsm6ds library
$(ADAFRUIT_LSM6DS): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_LSM6DS),adafruit-circuitpython-lsm6ds,$(ADAFRUIT_LSM6DS_VERSION),$(LIBDIR))

ADAFRUIT_MCP2515 ?= lib/adafruit_mcp2515
.PHONY: adafruit-mcp2515
adafruit-mcp2515: $(ADAFRUIT_MCP2515) ## Download the adafruit-circuitpython-mcp2515 library
$(ADAFRUIT_MCP2515): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_MCP2515),adafruit-circuitpython-mcp2515,$(ADAFRUIT_MCP2515_VERSION),$(LIBDIR))

ADAFRUIT_MCP9808 ?= lib/adafruit_mcp9808.py
.PHONY: adafruit-mcp9808
adafruit-mcp9808: $(ADAFRUIT_MCP9808) ## Download the adafruit-circuitpython-mcp9808 library
$(ADAFRUIT_MCP9808): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_MCP9808),adafruit-circuitpython-mcp9808,$(ADAFRUIT_MCP9808_VERSION),$(LIBDIR))

ADAFRUIT_NEOPIXEL ?= lib/neopixel.py
.PHONY: adafruit-neopixel
adafruit-neopixel: $(ADAFRUIT_NEOPIXEL) ## Download the adafruit-circuitpython-neopixel library
$(ADAFRUIT_NEOPIXEL): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_NEOPIXEL),adafruit-circuitpython-neopixel,$(ADAFRUIT_NEOPIXEL_VERSION),$(LIBDIR))

ADAFRUIT_OV5640 ?= lib/adafruit_ov5640
.PHONY: adafruit-ov5640
adafruit-ov5640: $(ADAFRUIT_OV5640) ## Download the adafruit-circuitpython-ov5640 library
$(ADAFRUIT_OV5640): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_OV5640),adafruit-circuitpython-ov5640,$(ADAFRUIT_OV5640_VERSION),$(LIBDIR))

ADAFRUIT_PCA9685 ?= lib/adafruit_pca9685.py
.PHONY: adafruit-pca9685
adafruit-pca9685: $(ADAFRUIT_PCA9685) ## Download the adafruit-circuitpython-pca9685 library
$(ADAFRUIT_PCA9685): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_PCA9685),adafruit-circuitpython-pca9685,$(ADAFRUIT_PCA9685_VERSION),$(LIBDIR))

ADAFRUIT_REGISTER ?= lib/adafruit_register
.PHONY: adafruit-register
adafruit-register: $(ADAFRUIT_REGISTER) ## Download the adafruit-circuitpython-register library
$(ADAFRUIT_REGISTER): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_REGISTER),adafruit-circuitpython-register,$(ADAFRUIT_REGISTER_VERSION),$(LIBDIR))

ADAFRUIT_RFM ?= lib/adafruit_rfm
.PHONY: adafruit-rfm
adafruit-rfm: $(ADAFRUIT_RFM) ## Download the adafruit-circuitpython-rfm library
$(ADAFRUIT_RFM): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_RFM),adafruit-circuitpython-rfm,$(ADAFRUIT_RFM_VERSION),$(LIBDIR))

ADAFRUIT_TICKS ?= lib/adafruit_ticks.py
.PHONY: adafruit-ticks
adafruit-ticks: $(ADAFRUIT_TICKS) ## Download the adafruit-circuitpython-ticks library
$(ADAFRUIT_TICKS): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_TICKS),adafruit-circuitpython-ticks,$(ADAFRUIT_TICKS_VERSION),$(LIBDIR))

ADAFRUIT_TCA9548A ?= lib/adafruit_tca9548a.py
.PHONY: adafruit-tca9548a
adafruit-tca9548a: $(ADAFRUIT_TCA9548A) ## Download the adafruit-circuitpython-tca9548a library
$(ADAFRUIT_TCA9548A): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_TCA9548A),adafruit-circuitpython-tca9548a,$(ADAFRUIT_TCA9548A_VERSION),$(LIBDIR))

ADAFRUIT_VEML7700 ?= lib/adafruit_veml7700.py
.PHONY: adafruit-veml7700
adafruit-veml7700: $(ADAFRUIT_VEML7700) ## Download the adafruit-circuitpython-veml7700 library
$(ADAFRUIT_VEML7700): $(LIBDIR)
	$(call install_lib,$(ADAFRUIT_VEML7700),adafruit-circuitpython-veml7700,$(ADAFRUIT_VEML7700_VERSION),$(LIBDIR))

define install_lib
	@test -s $(1) || { \
		pip install $(2)==$(3) --target $(4) --no-deps; \
		rm -rf $(4)/$(subst -,_,$(2))-$(3).dist-info; \
	}
endef
