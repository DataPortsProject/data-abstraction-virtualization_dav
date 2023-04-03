#!/bin/sh -e

scripts_dir='/opt/nifi/scripts'

# Run the common script to get utility functions
[ -f "${scripts_dir}/common.sh" ] && . "${scripts_dir}/common.sh"

# NIFI_HOME is defined by an ENV command in the backing Dockerfile
# Export custom.properties file at
export NIFI_VARIABLE_REGISTRY_PROPERTIES=${NIFI_HOME}/conf/custom.properties

# Establish vdc user properties
prop_replace 'nifi.vdc.metadata.http.port'        "${VDC_METADATA_PORT:-8801}"   ${NIFI_VARIABLE_REGISTRY_PROPERTIES}
prop_replace 'nifi.vdc.metadata.mongoDB.uri'      "${VDC_METADATA_MONGODB_URI}"  ${NIFI_VARIABLE_REGISTRY_PROPERTIES}
prop_replace 'nifi.vdc.service.http.port'         "${VDC_SERVICE_PORT:-8800}"    ${NIFI_VARIABLE_REGISTRY_PROPERTIES}
prop_replace 'nifi.vdc.service.spark.master.uri'  "${VDC_SPARK_MASTER_URI}"      ${NIFI_VARIABLE_REGISTRY_PROPERTIES}
prop_replace 'nifi.vdc.service.spark.rest.url'    "${VDC_SPARK_REST_URL}"        ${NIFI_VARIABLE_REGISTRY_PROPERTIES}
prop_replace 'nifi.vdc.ackApi.http.port'          "${VDC_ACK_API_PORT:-8802}"    ${NIFI_VARIABLE_REGISTRY_PROPERTIES}

# Run the nifi entrypoint
. "${scripts_dir}/start.sh"
