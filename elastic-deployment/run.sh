export net=elasticnet

docker network create $net
docker run -d --name elasticsearch --net $net -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:8.8.0
docker run -d --name kibana --net $net -p 5601:5601 kibana:8.8.0
