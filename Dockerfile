FROM python:3.11-alpine
WORKDIR /
COPY . .
CMD python -m http.server ${PORT:-8000}
