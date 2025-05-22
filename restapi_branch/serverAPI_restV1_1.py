#
# MODULE: REST API
#
# Script to expose the parsed SNMP values through a REST endpoint. -- Pull Mode --
# Server: Telemetry server (192.168.100.171)
# Script location: /home/uba/restapi_branch
# Logs location:
# Release: 30-04-2025 (V1)
# Current Version: V1_1            Release: 19-05-2025
    # Implementing Endpoints REST to return all and specific metrics V1_1
    # V1 -- MODULE: REST API --


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
    from get_viaSNMPV1_2 import getSnmp_value

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

# Creating the endpoints REST
#@app.route("/metrics", methods=["GET"])
#def all_metrics():
#	snmp_result = getSnmp_value()
#	return jsonify(snmp_result)

# Endpoint REST. Returns all the metrics (NE/OID). Calls the function without parameters
@app.route("/metrics", methods=["GET"])
def metricsAll():
    snmp_result = getSnmp_value()
    if not snmp_result or not isinstance(snmp_result, list):
        return jsonify({"error": "Unable to collect SNMP data"}), 500
    return jsonify(snmp_result)

# Endpoint REST. Returns the metrics for a specific NE. Calls the function with parameters
@app.route("/metrics/ne/<ne_name>", methods=["GET"])
def metricsBy_NE(ne_name):
    result = getSnmp_value(ne_filter=ne_name)
    if result:
        return jsonify(result)
    return jsonify({"error": f"No metrics found for NE '{ne_name}'"}), 404

# Endpoint REST. Returns the metrics for a metric name. Calls the function with parameters
@app.route("/metrics/metric/<metric_name>", methods=["GET"])
def metricsBy_Metric(metric_name):
    result = getSnmp_value(metric_filter=metric_name)
    if result:
        return jsonify(result)
    return jsonify({"error": f"No metrics found for metric '{metric_name}'"}), 404


if __name__ == "__main__":
    app.run(host=config["api"]["host"], port=config["api"]["port"])
