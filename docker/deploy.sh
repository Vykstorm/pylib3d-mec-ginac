

cd base \
&& sudo docker build . -t pylib3d-mec-ginac:latest \
&& cd ..

cd jupyter \
&& sudo docker build . -t pylib3d-mec-ginac-jupyter:latest \
&& cd ..

cd docs \
&& sudo docker build . -t pylib3d-mec-ginac-docs:latest \
&& cd ..
