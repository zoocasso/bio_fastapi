FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

COPY ./input_data /code/input_data

COPY ./static /code/static

COPY ./templates /code/templates
 
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "app.main_api:app", "--host", "0.0.0.0", "--port", "8000"]