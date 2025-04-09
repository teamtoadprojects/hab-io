FROM debian:bullseye-slim AS ssdv

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libssl-dev \
    libcurl4-openssl-dev \
    git \
    curl && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/fsphil/ssdv.git /ssdv
WORKDIR /ssdv

RUN make

FROM python:3.12

RUN python -m pip install pipx
RUN pipx install pipenv

WORKDIR /app

COPY . /app/

COPY --from=ssdv /ssdv/ssdv /usr/local/bin/ssdv

ENV PATH=$PATH:/root/.local/bin
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy --ignore-pipfile

ENTRYPOINT [ "/app/.venv/bin/python" ]
CMD [ "/app/core.py" ]
