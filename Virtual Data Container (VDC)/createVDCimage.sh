#!/bin/sh

# Build the 1.0 version of the VDC component docker image
docker build -t iccs/vdc:1.0 ./ -f docker/Dockerfile
