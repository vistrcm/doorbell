FROM python:3 as builder
COPY Pipfile.lock ./
RUN pip install pipenv && pipenv requirements > /requirements.txt

FROM python:3
RUN groupadd -r doorbell && useradd -d /app --no-log-init -r -g doorbell doorbell
WORKDIR /app
COPY --from=builder /requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY main.py ./
USER doorbell
CMD ["python", "main.py"]
