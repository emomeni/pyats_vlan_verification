from genie.testbed import load
from pyats import aetest
import sys
from unicon.core.errors import ConnectionError
import logging
from pyats.log.utils import banner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define VLANs to be checked
EXPECTED_VLANS = [int(vlan) for vlan in sys.argv[1:]] if len(sys.argv) > 1 else [11, 12, 13]

class CommonSetup(aetest.CommonSetup):
    """Setup Section: Connect to Devices"""

    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all devices listed in the testbed."""
        self.parent.parameters["devices"] = {}
        for device_name, device in testbed.devices.items():
            try:
                device.connect()
                self.parent.parameters["devices"][device_name] = device
                logger.info(banner(f"Successfully connected to {device_name}"))
            except ConnectionError as e:
                self.failed(f"Failed to connect to {device_name}: {e}", goto=['common_cleanup'])

class VLANVerificationTestcase(aetest.Testcase):
    """VLAN Verification Test Case"""

    @aetest.setup
    def setup(self, testbed):
        """Set up the test case by connecting to 'leaf1' and loading VLAN data."""
        self.device = testbed.devices.get("leaf1")
        if not self.device:
            self.failed("Device 'leaf1' not found in the testbed configuration.", goto=['cleanup'])
        try:
            self.device.connect()
            self.vlan_data = self.device.parse("show vlan")
        except Exception as e:
            self.failed(f"Failed to retrieve VLAN information from 'leaf1': {e}", goto=['cleanup'])

    @aetest.test
    def verify_vlans(self):
        """Check if the expected VLANs are present in the device."""
        missing_vlans = []
        vlan_list = [int(vlan["vlan_id"]) for vlan in self.vlan_data["vlans"].values()]
        for vlan in EXPECTED_VLANS:
            if vlan not in vlan_list:
                missing_vlans.append(vlan)
        
        assert not missing_vlans, f"Missing VLANs: {missing_vlans}"

    @aetest.cleanup
    def cleanup(self):
        """Cleanup by disconnecting the device."""
        try:
            if self.device.connected:
                self.device.disconnect()
                logger.info(banner(f"Disconnected from {self.device.name}"))
        except Exception as e:
            logger.warning(f"Failed to disconnect from {self.device.name}: {e}")

class CommonCleanup(aetest.CommonCleanup):
    """Common Cleanup Section"""

    @aetest.subsection
    def disconnect_from_devices(self):
        """Disconnect from all connected devices."""
        devices = self.parent.parameters.get("devices", {})
        for device in devices.values():
            try:
                if device.connected:
                    device.disconnect()
                    logger.info(banner(f"Disconnected from {device.name}"))
            except Exception as e:
                logger.warning(f"Failed to disconnect from {device.name}: {e}")

if __name__ == "__main__":
    # Load the testbed file (YAML) to connect to the devices
    try:
        testbed = load("testbed.yaml")
        aetest.main(testbed=testbed)
    except Exception as e:
        logger.error(f"Failed to load testbed or execute tests: {e}")