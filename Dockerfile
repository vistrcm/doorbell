FROM python:3.10 as builder
COPY Pipfile.lock ./
RUN pip install pipenv && pipenv requirements > /requirements.txt

FROM python:3.10
RUN groupadd -r doorbell && useradd -d /app --no-log-init -r -g doorbell doorbell
WORKDIR /app
COPY --from=builder /requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY main.py ./
USER doorbell
CMD ["python", "main.py"]
