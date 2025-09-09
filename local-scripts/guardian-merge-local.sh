#!/bin/bash

echo "Insira o número do Nó Guardião local:"
read mix_server

num_servers="3"
read -e -i "$num_servers" -p "Insira o número total de nós guardiões: " input
num_servers="${input:-$num_servers}"


curl -sS -X POST http://localhost:8080/guardian/merge-local \
    -d "serverId=$mix_server&numServers=$num_servers"