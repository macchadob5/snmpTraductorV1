#
# MODULE: SNMP Polling
# MODULE: Parser
#
# Script to connect to the Network Element (NE) and get values via SNMP. -- Pull Mode --
# Server: Telemetry server (192.168.100.171)
# Script location: /home/uba/snmp_parser_branch
# Logs location:
# Release: 03-04-2025 (V1)
# Current Version: V1_2            Release: 15-05-2025
    # Connect and get values via SNMP for multiple NEs and OIDs V1_2
    # Integration with TextFSM parser V1_1 -- MODULE: Parser --


# Importing modules
import subprocess
import yaml
import textfsm
import os
from datetime import datetime

# Declaring variables
configNE_File = "configNE_snmpV1_2.yaml"
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
#def getSnmp_value():
def getSnmp_value(ne_filter=None, metric_filter=None):
    configYAML = loadConfig_YAML()
    #snmpNE_conf = configYAML["snmp"]

    # List to save the parsed SNMP result and to be returned for use by the REST API
    snmp_forAPI = []

    # Reading the NE values from the YAML file. Using a for to read/load each NE
    for snmpNE in configYAML["snmp_NE"]:

        # Filter by NE name (if provided)
        if ne_filter and snmpNE["name"] != ne_filter:
            continue

        host = snmpNE["host"]
        community = snmpNE["community"]
        version = snmpNE.get("version", "2c")
        #oid = snmpNE["oid"]
        command = snmpNE.get("command", "snmpwalk")

        # Using a for to read/load each OID of that NE
        for oid_entry in snmpNE["oids"]:
            oid = oid_entry["oid"]
            metric_name = oid_entry.get("metric_name", "unknown_metric")

            # Filter by Metric name (if provided)
            if metric_filter and metric_name != metric_filter:
                continue

            # Builds the SNMP command with the arguments, executes it using subprocess.run and saves the result
            try:
                result = subprocess.run(
                    [command, "-v", version, "-c", community, host, oid], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)

                # Clean up the command output and print
                output = result.stdout.strip()
                #print("Output from NE via SNMP:", output)
                print(f"Output from {snmpNE['name']} ({host}) - OID {oid}: {output}")

                # Uses TextFSM parser to extract the SNMP values. Adds a timestamp
                parsed = parseSnmp_output(output)
                if parsed:
                    metric = int(parsed[0]["VALUE"])
                    timestamp = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

                    #Sorting the result for better presentation
                    parsed_sort = {
                    "NAME": snmpNE["name"],
                    "HOST": host,
                    "OID": parsed[0]["OID"],
                    "METRIC": metric_name,
                    "TYPE": parsed[0]["TYPE"],
                    "VALUE": parsed[0]["VALUE"],
                    "TIMESTAMP": timestamp
                    }
                    print(f"{metric_name}: {metric}")
                    print("Timestamp:", timestamp)
                    print("Parsed SNMP:", parsed_sort)

                    # Adding the result to the list
                    snmp_forAPI.append(parsed_sort)
                else:
                    print("No valid result found in the SNMP output.")
                    #return None
                #Use this OID to test this else section, YAML file
                #oid: ".1.3.6.1.4.1.2858.500.6.1.0" #OID for NE version

            # Exception if no response via SNMP
            except subprocess.CalledProcessError as e:
                #print("Failed to execute the SNMP command:", e)
                print(f"Failed to execute the SNMP command for {snmpNE['name']} - {oid}:", e)
                #return None

    # Returning the list. To be used by the REST API
    return snmp_forAPI

if __name__ == "__main__":
    getSnmp_value()
#    getSnmp_value(ne_filter="STP-SNC")
#    getSnmp_value(metric_filter="AspRxMsgTotal_SBLHSS01_1_Pref")
