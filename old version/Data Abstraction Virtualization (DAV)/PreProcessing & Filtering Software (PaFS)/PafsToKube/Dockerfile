FROM python:3.8.5

RUN mkdir /PafsToKube
WORKDIR /PafsToKube
ADD . /PafsToKube/
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/PafsToKube/pafs.py"]
