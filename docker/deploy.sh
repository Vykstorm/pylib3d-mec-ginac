

sudo docker build . -t pylib3d-mec-ginac:latest

cd jupyter \
&& sudo docker build . -t pylib3d-mec-ginac-jupyter:latest \
&& cd ..

cd docs \
&& sudo docker build . -t pylib3d-mec-ginac-docs:latest \
&& cd ..
