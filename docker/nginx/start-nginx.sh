#!/usr/bin/env bash

if [ -n "${HTTP_AUTH}" ]; then
  echo "Enabling HTTP Auth, using htpasswd file from the HTTP_AUTH env. variable."
  ln -s /etc/nginx/pycon-config-available/10-http-auth.inc.conf /etc/nginx/pycon-config-enabled/10-http-auth.inc.conf
  echo "${HTTP_AUTH}" > /etc/nginx/htpasswd
fi

exec nginx -g "daemon off;"
