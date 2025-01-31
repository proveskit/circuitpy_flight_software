"""
Test script for SD card functionality using the updated pysquared.py module.
"""

import os  # For filesystem operations and syncing
import time

from lib.pysquared.config import Config
from lib.pysquared.logger import Logger
from lib.pysquared.pysquared import Satellite


def main():
    # Set up the logger
    logger = Logger()
    logger.info("Testing SD Card Functionality")

    # Initialize the configuration
    config = Config()

    # Initialize the Satellite instance
    try:
        satellite = Satellite(config=config, logger=logger)
        logger.info("Satellite instance created successfully.")
    except Exception as e:
        logger.error("Failed to create Satellite instance.", err=str(e))
        return

    # Check if the 'hardware' attribute exists
    if not hasattr(satellite, "hardware"):
        logger.error("Satellite object has no 'hardware' attribute.")
        return

    # Check if the SD card was initialized successfully
    if satellite.hardware.get("SD Card", False):
        logger.info("SD card initialized successfully.")

        # Define a test file path
        test_file_path = "/sd/test_sd_functionality.txt"

        # Open the log file on SD card for appending
        try:
            logger.debug(f"Opening file for writing: {test_file_path}")
            # Use 'with' statement to ensure the file is properly closed
            with open(test_file_path, "a") as log_file:
                logger.log_file = log_file  # Redirect logger output to the file
                logger.info("Logger now writing to SD card")

                # Write a test message to the log
                logger.debug("This is a test message written to the log file.")

                # Flush and sync to ensure data is written
                log_file.flush()
                os.sync()

            # Reset logger's log_file after closing
            logger.log_file = None

        except Exception as e:
            logger.error("Failed to write to log file on SD card.", err=str(e))
            return

        # Read data back from the test file
        try:
            logger.debug(f"Opening file for reading: {test_file_path}")
            with open(test_file_path, "r") as f:
                data = f.read()
            logger.info(f"Data read from {test_file_path} successful")
            # For large data, avoid logging the entire content
            # Alternatively, print a small preview
            data_preview = data[:100] + "..." if len(data) > 100 else data
            print(f"Data read from {test_file_path}:\n{data_preview}")
        except Exception as e:
            logger.error("Failed to read from the SD card.", err=str(e))
            return

        # List files on the SD card
        try:
            logger.debug("Listing files on the SD card:")
            files = os.listdir("/sd")
            for file in files:
                logger.info(f"Found file: {file}")
        except Exception as e:
            logger.error("Failed to list files on the SD card.", err=str(e))

        # Wait a moment to ensure all operations complete
        logger.debug("Waiting for filesystem operations to complete...")
        time.sleep(2)

        # Unmount the SD card to ensure all data is written
        try:
            logger.debug("Unmounting SD card...")
            import storage

            storage.umount("/sd")
            logger.info("SD card unmounted successfully.")
        except Exception as e:
            logger.error("Failed to unmount SD card.", err=str(e))

    else:
        logger.error("SD card failed to initialize.")


if __name__ == "__main__":
    main()
