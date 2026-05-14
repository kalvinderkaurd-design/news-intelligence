FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt || true
RUN pip install --no-cache-dir flask gunicorn
COPY . .
ENV PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:8080 ${APP_MODULE:-app:app}"]
