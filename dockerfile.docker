FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir flask flask_sqlalchemy werkzeug
RUN mkdir -p /app/static/uploads /app/templates
EXPOSE 5000
CMD ["python", "app.py"]
