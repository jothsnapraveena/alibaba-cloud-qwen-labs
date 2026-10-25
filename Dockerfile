FROM python:3.12-slim
WORKDIR /app
COPY qwenlabs /app/qwenlabs
USER 65534:65534
ENTRYPOINT ["python", "-m", "qwenlabs.run"]
CMD ["9"]
