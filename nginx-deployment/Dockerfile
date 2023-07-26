FROM nginx:latest as runtime

ARG NGINX_PORT="80"

EXPOSE ${NGINX_PORT}

COPY ./sites-enabled.conf /etc/nginx/conf.d/sites-enabled.conf
