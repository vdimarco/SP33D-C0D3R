FROM python:3.11-slim
RUN pip install pytest pytest-timeout requests
WORKDIR /workspace
COPY run_tests.py /run_tests.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN mkdir -p /signals
ENTRYPOINT ["/entrypoint.sh"]
