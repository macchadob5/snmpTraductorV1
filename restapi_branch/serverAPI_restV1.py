#
# MODULE: REST API
#
# Script to expose the parsed SNMP values through a REST endpoint. -- Pull Mode --
# Server: Telemetry server (192.168.100.171)
# Script location: /home/uba/restapi_branch
# Logs location:
# Release: 30-04-2025 (V1)
# Current Version: V1            Release: 30-04-2025
    # MODULE: REST API


# Importing modules
import sys
import os
import yaml
from flask import Flask, jsonify

# Declaring variables
configAPI_File = "configAPI_rest.yaml"

# Adding the SNMP Polling module path
base_dir = os.path.dirname(__file__)
snmpModule_Path = os.path.abspath(os.path.join(base_dir, "..", "snmp_parser_branch"))
sys.path.insert(0, snmpModule_Path)
#print (snmpModule_Path)

# Importing the function getSnmp_value from the SNMP polling module
try:
    from get_viaSNMPV1_1 import getSnmp_value

# Exception if not able to import the function
except ImportError as e:
    print("Failed to import SNMP Polling module:", e)
    sys.exit(1)

# Function to load API config from YAML file
def loadConfigAPI_YAML():
    configAPI = os.path.join(os.path.dirname(__file__), configAPI_File)
    with open(configAPI) as result:
        return yaml.safe_load(result)

config = loadConfigAPI_YAML()
#print(config)

# Initialize the Flask application to handle the routes and HTTP requests
app = Flask(__name__)

# Creates dinamically the endpoint from the YAML file
@app.route(f"/{config['api']['endpoint_name']}", methods=["GET"])
def active_calls():
    snmp_result = getSnmp_value()
    if snmp_result and "VALUE" in snmp_result:
        return jsonify({
            "metric": "active_calls",
            "sourceOID": snmp_result.get("OID", "unknown"),
            "value": int(snmp_result["VALUE"]),
            "timestamp": snmp_result.get("TIMESTAMP")
        })
    else:
        return jsonify({"error": "Unable to collect SNMP data"}), 500

if __name__ == "__main__":
    app.run(host=config["api"]["host"], port=config["api"]["port"])
