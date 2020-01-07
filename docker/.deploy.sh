
PYTHON_VERSION=3.7
VERSION=1.0.0
BASE=pylib3d-mec-ginac:$VERSION

cd base \
&& sudo docker build . -t $BASE_IMAGE --build-arg PYTHON_VERSION=$PYTHON_VERSION \
&& cd ..

cd jupyter \
&& sudo docker build . -t pylib3d-mec-ginac-jupyter:$VERSION --build-arg BASE=$BASE \
&& cd ..

cd docs \
&& sudo docker build . -t pylib3d-mec-ginac-docs:$VERSION --build-arg BASE=$BASE \
&& cd ..
