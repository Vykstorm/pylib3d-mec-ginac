
export PYTHON_VERSION=3.7
export VERSION=1.0.0
export BASE=pylib3d-mec-ginac:$VERSION

# Build base docker image
cd base \
&& sudo docker build . -t $BASE --build-arg PYTHON_VERSION=$PYTHON_VERSION \
&& cd ..

# Build docker with jupyter server
cd jupyter \
&& sudo heroku container:push web -a pylib3d-mec-ginac --arg BASE=$BASE \
&& sudo heroku container:release web -a pylib3d-mec-ginac \
&& cd ..

# Build docker with html docs server
cd docs \
&& sudo heroku container:push web -a pylib3d-mec-ginac-docs --arg BASE=$BASE \
&& sudo heroku container:release web -a pylib3d-mec-ginac-docs \
&& cd ..

# Open both apps in the web
xdg-open https://pylib3d-mec-ginac.herokuapp.com/notebooks/Untitled.ipynb
xdg-open https://pylib3d-mec-ginac-docs.herokuapp.com
