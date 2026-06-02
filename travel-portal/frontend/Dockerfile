FROM python:3.11-slim

WORKDIR /app

# Install ONLY frontend-specific dependencies directly
RUN pip install --no-cache-dir \
    streamlit==1.32.0 \
    requests==2.31.0 \
    pandas==2.2.1

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

