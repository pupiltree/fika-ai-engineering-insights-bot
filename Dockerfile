FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Run main.py and Streamlit dashboard.py at once
CMD ["bash", "-c", "python main.py & streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0 && wait"]
