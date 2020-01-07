ARG BASE=pylib3d-mec-ginac:latest
FROM $BASE
ENV PORT=8000
# Install additional packages
RUN pip install matplotlib pandas
# Copy empty notebook
COPY Untitled.ipynb /pylib3d-mec-ginac/examples/Untitled.ipynb
# Docker will run python interpreter
CMD jupyter notebook --no-browser --port=$PORT --ip=$(hostname) --allow-root -y --notebook-dir=/pylib3d-mec-ginac/examples --NotebookApp.token='' --NotebookApp.password=''
