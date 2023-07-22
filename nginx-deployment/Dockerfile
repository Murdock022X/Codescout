
FROM nginx:latest as runtime

ARG CONF_FILE="default.conf"

ARG NGINX_PORT="80"

EXPOSE ${NGINX_PORT}

COPY ./default.conf /etc/nginx/conf.d
