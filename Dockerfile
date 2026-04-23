FROM python:3.10.19-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Build context is pddAnalysisDashboard directory
COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

# Same style as streamlit_server: explicit python, run app; port/address via env (compose)
ENTRYPOINT ["python3.10", "-m", "app"]
