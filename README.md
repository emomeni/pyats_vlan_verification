# VLAN Verification Test with PyATS

## Overview
This script is used to verify VLAN configurations on Cisco NX-OS Switches using the Cisco PyATS and Genie framework. It connects to network devices defined in a testbed file, retrieves VLAN information, and ensures that the expected VLANs are configured correctly.

The script contains setup, test, and cleanup sections to automate the process of verifying VLAN configurations, making it efficient and reliable for network validation.

## Prerequisites
- Python 3.x installed.
- Cisco PyATS and Genie libraries installed.
- A testbed YAML file (`testbed.yaml`) that defines the network devices to be tested.
- Proper access to the devices defined in the testbed.

## Installation (required)
To install the necessary Python libraries, run:

```bash
pip install pyats genie
```

## Steps to Clone:
1. **Clone the repo**
```bash
git clone https://github.com/emomeni/pyats_vlan_verification.git
```

2. **Go to your project directory**
```bash
cd pyats_vlan_verification
```

3. **Set up a Python virtual environment**
First make sure that you have Python 3 installed on your machine. We will then be using venv to create an isolated environment with only the necessary packages.

3.1. **Install virtualenv via pip**
```bash
pip install virtualenv
```

3.2. **Create the venv**
```bash
python3 -m venv venv
```

3.3. **Activate your venv**
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Script Details
In the following, we have different sections of the code.

### Key Components
* CommonSetup Class: Connects to all devices in the testbed before running the test cases.
    *  The connect_to_devices method attempts to connect to each device and logs the connection status.
    * Connects to all devices defined in the testbed YAML file.
    * Stores the connected devices in self.parent.parameters['devices'].
    * Logs a message upon a successful connection.
    * Fails the script if it cannot connect to a device.

* VLANVerificationTestcase Class: Contains the setup, test, and cleanup methods for verifying VLAN configurations.
    * Setup: Connects to a specific device (leaf1) and loads VLAN information.
        * Attempts to get a specific device (leaf1) from the testbed.
        * If the device is not found, it fails the setup.
        * Runs the show vlan command to get VLAN data and parses the output.
        * If parsing fails, the setup is marked as failed.
    
    * Test (verify_vlans): Verifies if all the expected VLANs are present on the device. If any VLANs are missing, the test fails.
        * Verifies that all expected VLANs (EXPECTED_VLANS) are present in the device's VLAN configuration.
        * Converts VLAN IDs from the parsed output to integers and stores them in vlan_list.
        * If any expected VLAN is missing, it adds it to missing_vlans.
        * Uses an assert statement to raise an error if there are any missing VLANs.

    * Cleanup: Disconnects from the device after verification.
        * Disconnects from leaf1.
        * Logs a message to confirm disconnection.
        * Logs a warning if disconnection fails.

* CommonCleanup Class: Disconnects from all devices connected during the test.
    * Disconnects from all devices connected during CommonSetup.
    * Logs a message to indicate that each device has been disconnected.
    * Logs a warning if it cannot disconnect from a device.

### Command-Line Arguments
* You can provide the list of VLANs to verify as command-line arguments.
* If no arguments are provided, the default VLANs `[11, 12, 13]` will be used.

### Running the Script
1. Ensure you have a valid `testbed.yaml` file that defines your network devices.
2. Run the script as follows:
```bash
python vlan_verification.py [vlan_id1 vlan_id2 ...]
```

For example, to verify VLANs 20, 30, and 40:
```bash
python vlan_verification.py 20 30 40
```

### Output
* The script logs the connection status to each device, the verification of VLANs, and the cleanup process.
* If any VLANs are missing, it raises an assertion error indicating which VLANs were not found.

### Logging
* The script uses Python's logging library to log information, warnings, and errors.
* Log messages are printed to the console, providing real-time updates on the script's progress.

### Cleanup
* The script ensures that all devices are properly disconnected at the end of the test, either through the test case cleanup or the common cleanup section.

### Troubleshooting
* Connection Errors: Ensure that the devices are accessible over the network and that credentials are correct in the `testbed.yaml` file.
* Missing VLANs: If the script reports missing VLANs, verify the network configuration manually to confirm if the VLANs are properly configured.

## Usage
This script is a useful tool for automating VLAN configuration checks on network devices. By leveraging PyATS and Genie, it provides a robust way to validate network configurations, helping network engineers ensure that their network is set up correctly.

## License
This project is licensed under the MIT License.