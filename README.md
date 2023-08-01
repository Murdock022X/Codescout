# Codescout

Codescout is an application that can be deployed via containerization for a specific organization that wishes to have complete control of their IP while still being able to keep a well documented, widely available, and searchable database of their IP.

Codescout has two primary services as part of it, these are the Codescout Flask deployment and the PostgreSQL database that facilitates its use. Elasticsearch is what gives Codescout the ability to function. In order to add data and search that data your organization must have an Elasticsearch cluster setup and connected to Codescout. There will also be an option to deploy an Elasticsearch cluster with Docker Compose for a demo purposes. Additionally Nginx may be added to function as a proxy to the webserver.