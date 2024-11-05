from genie.testbed import load
from pyats import aetest
import sys
import time
from unicon.core.errors import ConnectionError
import logging
from pyats.log.utils import banner
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of VLANs you intended to create (can also be passed as command-line arguments or environment variables)
EXPECTED_VLANS = [int(vlan) for vlan in os.getenv('EXPECTED_VLANS', '11,12,13').split(',')] if len(sys.argv) == 1 else [int(vlan) for vlan in sys.argv[1:]]

class CommonSetup(aetest.CommonSetup):
    """Common Setup Section"""
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all devices in the testbed with retry logic"""
        self.parent.parameters["devices"] = {}
        for device_name, device in testbed.devices.items():
            for attempt in range(3):  # Retry mechanism
                try:
                    device.connect()
                    self.parent.parameters["devices"][device_name] = device
                    logger.info(banner(f"Connected to {device_name}"))
                    break
                except ConnectionError as e:
                    logger.warning(f"Attempt {attempt + 1} failed to connect to device {device_name}: {e}")
                    if attempt == 2:  # Last attempt failed
                        self.failed(f"Failed to connect to device {device_name} after 3 attempts.")
                    time.sleep(5)  # Wait before retrying

class VLANVerificationTestcase(aetest.Testcase):
    """VLAN Verification Test Case"""
    @aetest.setup
    def setup(self, testbed):
        """Connect to the device and load VLAN information"""
        self.device = testbed.devices.get("leaf1")
        if not self.device:
            self.failed("Device 'leaf1' not found in the testbed.")
        
        try:
            logger.info(f"Parsing VLAN information on device {self.device.name}")
            self.vlan_data = self.device.parse("show vlan")
        except Exception as e:
            self.failed(f"Failed to parse VLAN information: {e}")

    @aetest.test
    def verify_vlans(self):
        """Verify that all the expected VLANs are present"""
        try:
            vlan_list = [int(vlan["vlan_id"]) for vlan in self.vlan_data["vlans"].values()]
            missing_vlans = [vlan for vlan in EXPECTED_VLANS if vlan not in vlan_list]
            assert len(missing_vlans) == 0, f"Missing VLANs: {missing_vlans}"
            logger.info(f"All expected VLANs {EXPECTED_VLANS} are present on the device.")
        except KeyError as e:
            self.failed(f"Failed during VLAN verification due to incorrect data format: {e}")
        except AssertionError as e:
            self.failed(str(e))

    @aetest.cleanup
    def cleanup(self):
        """Cleanup Section"""
        if self.device.is_connected():
            try:
                self.device.disconnect()
                logger.info(banner(f"Disconnected from {self.device.name}"))
            except Exception as e:
                logger.warning(f"Failed to disconnect device {self.device.name}: {e}")

class CommonCleanup(aetest.CommonCleanup):
    """Common Cleanup Section"""
    @aetest.subsection
    def disconnect_from_devices(self):
        """Disconnect from all devices."""
        devices = self.parent.parameters.get("devices", {})
        if devices:
            for device in devices.values():
                if device.is_connected():
                    try:
                        device.disconnect()
                        logger.info(banner(f"Disconnected from {device.name}"))
                    except Exception as e:
                        logger.warning(f"Failed to disconnect device {device.name}: {e}")

if __name__ == "__main__":
    # Load the testbed file (YAML) to connect to the devices
    try:
        testbed = load("testbed.yaml")
        aetest.main(testbed=testbed)
    except Exception as e:
        logger.error(f"Failed to load testbed: {e}")
        sys.exit(1)