FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 5000
CMD ["sh", "-c", "sleep 5 && python run.py --host=0.0.0.0"]