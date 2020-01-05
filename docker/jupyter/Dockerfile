ARG BASE=pylib3d-mec-ginac:latest
FROM $BASE
# Install additional packages
RUN pip install matplotlib pandas
# Copy empty notebook
COPY Untitled.ipynb /pylib3d-mec-ginac/examples/Untitled.ipynb
# Copy jupyter configuration
COPY config.py /jupyter-config.py
# Docker will run python interpreter
CMD jupyter notebook --no-browser --port=$PORT --ip=$(hostname) --allow-root -y --notebook-dir=/pylib3d-mec-ginac/examples --config /jupyter-config.py
