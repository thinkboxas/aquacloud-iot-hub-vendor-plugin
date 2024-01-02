FROM thinkboxas/aquacloud_common:v1-1.0.0
WORKDIR /app/aquacloud-iot-hub-vendor-plugin
COPY ./requirements.txt /app/aquacloud-iot-hub-vendor-plugin/requirements.txt
RUN pip install -r requirements.txt
COPY . /app/aquacloud-iot-hub-vendor-plugin
CMD ["python3", "main.py"]