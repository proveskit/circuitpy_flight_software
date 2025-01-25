import gc


class Face:
    def __init__(self, Add, Pos, debug_state, tca, logger):
        self.tca = tca
        self.address = Add
        self.position = Pos
        self.debug = debug_state
        self.logger = logger

        # Use tuple instead of list for immutable data
        self.senlist = ()
        # Define sensors based on position using a dictionary lookup instead of if-elif chain
        sensor_map = {
            "x+": ("MCP", "VEML", "DRV"),
            "x-": ("MCP", "VEML"),
            "y+": ("MCP", "VEML", "DRV"),
            "y-": ("MCP", "VEML"),
            "z-": ("MCP", "VEML", "DRV"),
        }
        self.senlist = sensor_map.get(Pos, ())

        # Initialize sensor states dict only with needed sensors
        self.sensors = {sensor: False for sensor in self.senlist}

        # Initialize sensor objects as None
        self.mcp = None
        self.veml = None
        self.drv = None

    def Sensorinit(self, senlist, address):
        gc.collect()  # Force garbage collection before initializing sensors

        if "MCP" in senlist:
            try:
                import lib.adafruit_mcp9808 as adafruit_mcp9808

                self.mcp = adafruit_mcp9808.MCP9808(self.tca[address], address=27)
                self.sensors["MCP"] = True
            except Exception as e:
                self.logger.error("Error Initilizating Temperature Sensor", err=e)

        if "VEML" in senlist:
            try:
                import lib.adafruit_veml7700 as adafruit_veml7700

                self.veml = adafruit_veml7700.VEML7700(self.tca[address])
                self.sensors["VEML"] = True
            except Exception as e:
                self.logger.error("Error Initilizating Light Sensor", err=e)

        if "DRV" in senlist:
            try:
                import lib.adafruit_drv2605 as adafruit_drv2605

                self.drv = adafruit_drv2605.DRV2605(self.tca[address])
                self.sensors["DRV"] = True
            except Exception as e:
                self.logger.error("Error Initilizating Motor Driver", err=e)

        gc.collect()  # Clean up after initialization


class AllFaces:
    def __init__(self, debug, tca, logger):
        self.tca = tca
        self.debug = debug
        self.faces = []
        self.logger = logger

        # Create faces using a loop instead of individual variables
        positions = [("y+", 0), ("y-", 1), ("x+", 2), ("x-", 3), ("z-", 4)]
        for pos, addr in positions:
            face = Face(addr, pos, debug, tca, self.logger)
            face.Sensorinit(face.senlist, face.address)
            self.faces.append(face)
            gc.collect()  # Clean up after each face initialization

    def Face_Test_All(self):
        results = []
        for face in self.faces:
            if face:
                try:
                    temp = face.mcp.temperature if face.sensors.get("MCP") else None
                    light = face.veml.lux if face.sensors.get("VEML") else None
                    results.append([temp, light])
                except Exception:
                    results.append([None, None])
        return results
