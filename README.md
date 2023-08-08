# Codescout

Codescout is an application that can be deployed via containerization for a 
specific organization that wishes to have complete control of their IP while 
still being able to keep a well documented, widely available, and searchable 
database of their IP.

Codescout has two primary services as part of it, these are the Codescout 
Flask deployment and the PostgreSQL database that facilitates its use. 
Additionally there is an Elasticsearch deployment included for demo purposes.
Elasticsearch is what gives Codescout the ability to function. In order to 
add data and search that data your organization must have an Elasticsearch 
cluster setup and connected to Codescout.

## Prerequisites

Have Docker installed and setup.

## Getting Started

1. Clone this repository and change directory to the repository.

```
git clone https://github.com/Murdock022X/Distributed-Code-Repositories
```

2. Deploy using the docker-compose.yml file. 

```
docker-compose up
```

## What I Learned

- ElasticSearch Architecture and Operations
- Furthered my knowledge of Docker and Docker-Compose, by learning how to 
automate Docker operation via Docker-Compose.
- Advanced in SQL operations by learning how relations work in SQL.
- Solidified my Flask programming.
- General deployment operations, experimented with Elasticsearch certs and 
verifying client.
