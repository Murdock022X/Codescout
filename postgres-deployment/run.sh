#!/bin/sh

docker run -d -v postgres_data:/var/lib/postgresql/data --name postgres --env-file=db.env -p 5432:5432 postgres
