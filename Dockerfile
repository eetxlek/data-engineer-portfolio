FROM apache/spark:3.5.3-python3

USER root

# Instalar dependencias Python del pipeline
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER spark