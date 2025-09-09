#!/bin/bash

echo "Insira o número do Nó Guardião local:"
read mix_server

num_servers="3"
read -e -i "$num_servers" -p "Insira o número total de nós guardiões: " input
num_servers="${input:-$num_servers}"

session_id="GuardianSession"
read -e -i "$session_id" -p "Insira o ID da sessão: " input
session_id="${input:-$session_id}"

election_name="Guardian_Election"
read -e -i "$election_name" -p "Insira o nome da eleição: " input
election_name="${input:-$election_name}"

curl -sS -X POST http://localhost:8080/guardian/setup-local \
    -d "serverId=$mix_server&numServers=$num_servers&sessionId=$session_id&electionName=$election_name"