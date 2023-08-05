FROM nginx:latest as runtime

ARG NGINX_PORT="80"

EXPOSE ${NGINX_PORT}

RUN rm /etc/nginx/conf.d/default.conf

COPY ./nginx.conf /etc/nginx/conf.d/nginx.conf
