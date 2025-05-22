# SNMP Traductor

This project implements an SNMP Traductor (middleware) that polls production Network Elements (NEs) via SNMP, parses the retrieved data, and exposes it through REST APIs and telemetry compatible interfaces.

A lot of NEs deployed in production telecom environments such as Softswitch, SBC (Session Border Controller), STP (Signal Transfer Point), DR (Diameter Router), etc., lack native support for telemetry protocols or YANG-based data models. This middleware acts as a translator, enabling these NEs to:
	- Integrate into modern observability pipelines.
	- Push metrics to time-series databases like InfluxDB.
	- Trigger alerting mechanisms via email or webhooks.
	- Feed real-time data into visualization platforms such as Grafana.

This Thesis aims to bridge NEs which rely solely on SNMP, with modern monitoring, alerting and visualization platforms.


Components:

--
1. SNMP Polling
--
- Tool: snmpwalk (via subprocess)
- Pulls metrics from SNMP OIDs
- Configurable via YAML (host, OID, community, etc.)
- Supports multiple NEs and multiple OIDs per NE
- Supports filtering by NE or metric name
- Pull mode

--
2. Parser
--
- Tool: TextFSM using a template
- Extracts values from SNMP raw output
- Appends metadata (NE name, IP, timestamp, metric name)
- Returns standardized JSON object

--
3. REST API
--
- Tool: Flask
- Exposes parsed SNMP values through a REST endpoint
- Configurable via YAML (host, port, endpoint)
- Supports:
	- Method GET /metrics - Returns all the metrics (NE/OID)
	- Method GET /metrics/ne/<ne_name> - Returns the metrics for a specific NE
	- Method GET /metrics/metric/<metric_name> - Returns the metrics for a metric name
- Pull mode