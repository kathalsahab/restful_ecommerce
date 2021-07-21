FROM python:3.8

WORKDIR /app

COPY Pipfile* ./

RUN pip install pipenv

RUN pipenv install --system --deploy --ignore-pipfile

COPY ecom ./ecom
COPY migrations ./migrations


ENV FLASK_RUN_HOST 0.0.0.0

CMD flask db upgrade && flask ecom deploy && flask run