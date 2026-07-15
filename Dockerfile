FROM python:3.11-alpine
WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["python", "-u", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
