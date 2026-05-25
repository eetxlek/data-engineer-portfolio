FROM apache/spark:3.5.3-python3

USER root

ENV PATH="/opt/spark/bin:$PATH"

# Instalar dependencias Python del pipeline
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Delta Lake sin arrastrar pyspark (ya incluido en la imagen base)
RUN pip install --no-cache-dir --no-deps delta-spark==3.2.0

# Configuración Spark con Delta Lake
COPY spark-defaults.conf /opt/spark/conf/spark-defaults.conf

USER spark