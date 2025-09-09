#!/bin/bash

echo "Insira o número do Nó de Mixagem local:"
read mix_server

num_servers="3"
read -e -i "$num_servers" -p "Insira o número total de nós de mixagem: " input
num_servers="${input:-$num_servers}"

curl -sS -X POST http://localhost:8080/shuffler/merge-local \
    -d "serverId=$mix_server&numServers=$num_servers"