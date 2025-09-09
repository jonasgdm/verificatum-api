#!/bin/bash

echo "Insira o número do Mix Server local:"
read mix_server

curl -sS -X POST http://localhost:8080/guardian/decrypt-local-async \
    -d "serverId=$mix_server"