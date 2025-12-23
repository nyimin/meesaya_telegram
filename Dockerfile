FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway provides the PORT environment variable
ENV PORT=8000
EXPOSE $PORT

# 1. Initialize DB (Create tables/Seed data)
# 2. Start Server on the correct PORT
CMD sh -c "python init_db.py && uvicorn main:app --host 0.0.0.0 --port ${PORT}"