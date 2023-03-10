# syntax=docker/dockerfile:1

FROM python:3.9-slim

RUN apt update && apt install -y curl

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

# Install latest version of poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY . /app/

RUN poetry config virtualenvs.create false
RUN --mount=type=cache,target=~/.cache/pypoetry/cache \
    --mount=type=cache,target=~/.cache/pypoetry/artifacts \
    poetry install --no-cache

CMD [ "python", "model_deployment_app/main.py" ]