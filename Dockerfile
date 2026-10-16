FROM python:3.12-slim

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* README.md ./
COPY src ./src

RUN poetry install --no-ansi --only main

COPY config_*.yaml ./
COPY run_*.sh ./
RUN chmod +x run_*.sh

ENV PATH="/app:${PATH}"

# Show available commands when the container is started without args
CMD ["python", "-c", "import importlib.metadata as m; print('IA data format converter image. Available commands:'); [print(f'  {e.name}') for e in m.entry_points(group='console_scripts') if e.dist.name=='ia-data-format-converter']"]
