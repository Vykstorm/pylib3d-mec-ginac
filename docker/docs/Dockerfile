ARG BASE=pylib3d-mec-ginac:latest
FROM $BASE
ENV PORT=7000
# Install sphinx & generate docs
RUN pip install -U sphinx \
    && cd pylib3d-mec-ginac/docs \
    && make html
# Now serve html docs in a server
CMD python -m http.server $PORT --bind $(hostname) --directory /pylib3d-mec-ginac/docs/_build/html
