FROM python:3.12

RUN python -m pip install pipx
RUN pipx install pipenv

WORKDIR /app

COPY . /app/

ENV PATH=$PATH:/root/.local/bin
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy --ignore-pipfile

ENTRYPOINT [ "/app/.venv/bin/python" ]
CMD [ "/app/core.py" ]
