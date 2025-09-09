#!/bin/bash

echo "Insira o número do Nó de Mixagem local:"
read mix_server

curl -sS -X POST http://localhost:8080/shuffler/shuffle-local \
    -d "serverId=$mix_server"