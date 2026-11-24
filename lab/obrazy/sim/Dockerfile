FROM python:3.13-slim
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin sim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY wtsim ./wtsim
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "wtsim.brama"]
CMD ["python", "-m", "wtsim.cnc"]
