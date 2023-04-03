FROM python:3.8.5

RUN mkdir /VdcToKube
WORKDIR /VdcToKube
ADD . /VdcToKube/
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/VdcToKube/vdc.py"]
