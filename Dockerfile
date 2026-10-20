FROM python:3.12-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY templates ./templates
COPY static ./static

# settings come from the environment at run time (docker run --env-file .env), never from the image
RUN useradd --create-home app && mkdir -p /code/input_data && chown app /code/input_data
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
