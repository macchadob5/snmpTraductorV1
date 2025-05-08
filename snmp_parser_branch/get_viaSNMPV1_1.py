#
# MODULE: SNMP Polling
# MODULE: Parser
#
# Script to connect to the Network Element (NE) and get values via SNMP. -- Pull Mode --
# Server: Telemetry server (192.168.100.171)
# Script location: /home/uba/snmp_parser_branch
# Logs location:
# Release: 03-04-2025 (V1)
# Current Version: V1.1            Release: 15-04-2025
    # Integration with TextFSM parser  -- MODULE: Parser --


# Importing modules
import subprocess
import yaml
import textfsm
import os
from datetime import datetime

# Declaring variables
configNE_File = "configNE_snmp.yaml"
parserTextFSM_Template = "snmpResponse_parser.template"

# Function to load SNMP config from YAML file
def loadConfig_YAML():
    configNE = os.path.join(os.path.dirname(__file__), configNE_File)
    with open(configNE) as result:
        return yaml.safe_load(result)
#readingYAML = loadConfig_YAML()
#print(readingYAML)

# Function to parse the SNMP response using TextFSM
def parseSnmp_output(output):
    templateTextFSM = os.path.join(os.path.dirname(__file__), parserTextFSM_Template)
    with open(templateTextFSM) as result:
        fsm = textfsm.TextFSM(result)
        data_parsed = fsm.ParseText(output)
        return [dict(zip(fsm.header, row)) for row in data_parsed]
#snmpTest = "SNMPv2-SMI::enterprises.2858.500.4.1.0 = INTEGER: 114"
#parsing = parseSnmp_output(snmpTest)
#print(parsing)

# Function for SNMP polling
def getSnmp_value():
    configYAML = loadConfig_YAML()
    snmpNE_conf = configYAML["snmp"]

    # Reading the values from the snmp_config.yaml file
    host = snmpNE_conf["host"]
    community = snmpNE_conf["community"]
    version = snmpNE_conf.get("version", "2c")
    oid = snmpNE_conf["oid"]
    command = snmpNE_conf.get("command", "snmpwalk")

    # Builds the SNMP command with the arguments and executes it using subprocess.run
    try:
        result = subprocess.run(
            [command, "-v", version, "-c", community, host, oid], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)

        # Clean up the command output and print
        output = result.stdout.strip()
        print("Output from NE via SNMP:", output)

        # Uses TextFSM parser to extract the SNMP values
        parsed = parseSnmp_output(output)
        if parsed:
            metric = int(parsed[0]["VALUE"])
            timestamp = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
            parsed[0]["TIMESTAMP"] = timestamp
            print("active_calls:", metric)
            print("Timestamp:", timestamp)
            print("Parsed SNMP:", parsed[0])
            return parsed[0]
        else:
            print("No valid result found in the SNMP output.")
            return None
        #Use this OID to test this else section, YAML file
        #oid: ".1.3.6.1.4.1.2858.500.6.1.0" #OID for NE version

    # Exception if no response via SNMP
    except subprocess.CalledProcessError as e:
        print("Failed to execute the SNMP command:", e)
        return None

if __name__ == "__main__":
    getSnmp_value()
