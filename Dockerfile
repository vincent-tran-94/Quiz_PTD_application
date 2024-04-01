FROM python:3.11-slim
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 9400
CMD ["python3","app.py","9400"]
