# PyCon CZ webpage
### How to run on localhost

#### Prerequisites
For local development you only need to install Docker. Tested on version 23.0.2. 

For Docker installation manuals check the following links:
* Ubuntu - install Docker engine using the [apt repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and add user to `docker` group as described [here](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) so you can run Docker locally as non-root user
* Windows & Mac - you can use Docker Desktop, check out [this](https://docs.docker.com/desktop/install/windows-install/) manual for Windows and [this](https://docs.docker.com/desktop/install/mac-install/) for Mac 

#### Setup
1. Build an image
```bash
make build
```
2. Run dev stack
```bash
make up
```
3. You can stop the server by pressing Ctrl+C and removing containers afterwards
```bash
make down 
```

In case you want to access admin page, either Django or Wagtail ones, you need to create a superuser and log in with its credentials:
```bash
make create-user
```

The development server runs at the address http://0.0.0.0:8000/, admin at http://0.0.0.0:8000/xx/admin and Wagtail admin at http://0.0.0.0:8000/xx/wagtail.



