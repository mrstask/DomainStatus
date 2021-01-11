FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install postgresql-client -y
EXPOSE 8023
CMD python app.py