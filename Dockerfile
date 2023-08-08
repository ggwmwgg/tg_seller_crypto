FROM python:3
ENV PYTHONUNBUFFERED=1
LABEL authors="GGwM"
WORKDIR /telegram_seller
COPY . /telegram_seller
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "app.py"]