
# Build base docker image
sudo docker build . -t pylib3d-mec-ginac:latest

# Build docker with jupyter server
cd jupyter \
&& sudo heroku container:push web -a pylib3d-mec-ginac \
&& sudo heroku container:release web -a pylib3d-mec-ginac \
&& cd ..

# Build docker with html docs server
cd docs \
&& sudo heroku container:push web -a pylib3d-mec-ginac-docs \
&& sudo heroku container:release web -a pylib3d-mec-ginac-docs \
&& cd ..

# Open both apps in the web
xdg-open https://pylib3d-mec-ginac.herokuapp.com/notebooks/Untitled.ipynb
xdg-open https://pylib3d-mec-ginac-docs.herokuapp.com
