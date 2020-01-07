
PYTHON_VERSION=3.7
VERSION=1.0.0

IMAGE_PREFIX=docker.pkg.github.com/vykstorm/pylib3d-mec-ginac
BASE=$IMAGE_PREFIX/pylib3d-mec-ginac:$VERSION

cd base \
&& sudo docker build . -t $BASE --build-arg PYTHON_VERSION=$PYTHON_VERSION \
&& cd ..

cd jupyter \
&& IMAGE=$IMAGE_PREFIX/pylib3d-mec-ginac-jupyter:$VERSION \
&& sudo docker build . -t $IMAGE --build-arg BASE=$BASE \
&& sudo docker push $IMAGE \
&& cd ..

cd docs \
&& IMAGE=$IMAGE_PREFIX/pylib3d-mec-ginac-docs:$VERSION \
&& sudo docker build . -t $IMAGE --build-arg BASE=$BASE \
&& sudo docker push $IMAGE \
&& cd ..
