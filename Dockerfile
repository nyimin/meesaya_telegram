FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway provides the PORT environment variable
ENV PORT=8000
EXPOSE $PORT

# 1. Run Migrations
# 2. Seed Data (optional, but good for fresh install)
# 3. Start Server
CMD sh -c "alembic upgrade head && python seed_data.py && uvicorn main:app --host 0.0.0.0 --port ${PORT}"