FROM python:3.12-alpine
RUN adduser -D -u 10001 app
WORKDIR /app
COPY app.py /app/
USER 10001
EXPOSE 8080
CMD ["python", "app.py"]