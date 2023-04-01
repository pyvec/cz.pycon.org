# PyCon CZ webpage
### How to run on localhost

#### Prerequisites: 
* docker-compose version 1.29.2 (for the time being, will be upgraded to v.2 ASAP)

#### Setup
1. Build an image
```bash
make build
```
2. Run dev stack
```bash
make up
```

In case you want to access admin page, either Django or Wagtail ones, you need to create a superuser and log in with its credentials:
```bash
make create-user
```

The development server runs at the address http://0.0.0.0:8000/, team admin at http://0.0.0.0:8000/team/admin and Wagtail admin at http://0.0.0.0:8000/team/wagtail for the time being. 



