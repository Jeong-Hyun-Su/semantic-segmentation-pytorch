FROM pytorch/pytorch:1.2-cuda10.0-cudnn7-runtime

WORKDIR ./semantic

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
