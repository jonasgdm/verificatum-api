#!/bin/bash

echo "Insira o número do Mix Server local:"
read mix_server

curl -sS -X POST http://localhost:8080/guardian/setup-local \
    -d "serverId=$mix_server&numServers=3&sessionId=GuardianSession&electionName=Guardian_Election"