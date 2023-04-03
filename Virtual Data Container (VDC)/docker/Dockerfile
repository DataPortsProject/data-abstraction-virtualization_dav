# Create the VDC image from apache's Nifi image
FROM apache/nifi:latest

# Copy VDC's templates
RUN mkdir $NIFI_HOME/conf/templates/
COPY ./nifi_templates/vdc_metadata_api.xml $NIFI_HOME/conf/templates/vdc_metadata_api.xml
COPY ./nifi_templates/vdc_with_spark.xml $NIFI_HOME/conf/templates/vdc_with_spark.xml
COPY ./nifi_templates/ack_vdc_api.xml $NIFI_HOME/conf/templates/ack_vdc_api.xml

# Copy conf/custom.properties template file
COPY ./docker/custom.properties $NIFI_HOME/conf/custom.properties

# Copy startVDC.sh file
COPY ./docker/startVDC.sh /opt/nifi/scripts/startVDC.sh

# Start from Nifi's entrypoint
ENTRYPOINT ["../scripts/startVDC.sh"]
