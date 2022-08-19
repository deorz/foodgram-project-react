FROM python:3.8.9

LABEL author='deorz' version=1 project='foodgram'

WORKDIR backend/

COPY requirements.txt requirements.txt

COPY data/ data/

RUN pip3 install -U pip && pip3 install -r requirements.txt

WORKDIR foodgram/

COPY foodgram/ .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]