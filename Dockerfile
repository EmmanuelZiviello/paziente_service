#BUILD STAGE
FROM python:3.9.18-bookworm
WORKDIR /
COPY ./requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./setup.py ./setup.py
COPY ./flaskr ./flaskr
RUN pip install -e .

#RUN STAGE

CMD ["/bin/bash", "-c", "flask --app flaskr run --host=0.0.0.0"]