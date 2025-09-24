#!/bin/bash

echo "Insira o número do Nó Guardião local:"
read mix_server

curl -sS -X POST http://localhost:8080/guardian/decrypt-local \
    -d "serverId=$mix_server"