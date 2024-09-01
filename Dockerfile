FROM python:3.10-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libportaudio2 \
    libasound-dev \
    ffmpeg \
    wget

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install Cython

RUN python setup.py build_ext --inplace

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libportaudio2 \
    libasound-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN find . -name "*.py" -type f -not -path "./core/plugins/*" -delete

EXPOSE 8000

ENV PYTHONPATH=/app:$PYTHONPATH

CMD ["uvicorn", "core.server:app", "--host", "0.0.0.0", "--port", "8000"]