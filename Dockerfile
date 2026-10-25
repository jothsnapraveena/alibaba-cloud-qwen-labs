FROM python:3.12-slim
WORKDIR /app
RUN mkdir /data && chown 65534:65534 /data
COPY qwenlabs /app/qwenlabs
ENV PYTHONDONTWRITEBYTECODE=1
USER 65534:65534
ENTRYPOINT ["python", "-m", "qwenlabs.run"]
CMD ["9"]
