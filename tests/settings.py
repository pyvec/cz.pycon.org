from settings import *

DATABASES = {
    "default": dj_database_url.parse("sqlite://:memory:"),
}
