FROM python:3.13

ENV PYTHONUNBUFFERED=1

WORKDIR  /var/django-app

RUN pip install --upgrade pip "poetry==2.2.1"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY mysite .

CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]