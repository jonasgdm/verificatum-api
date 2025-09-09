#!/bin/bash

echo "Insira o número do Nó de Mixagem local:"
read mix_server

num_servers="3"
read -e -i "$num_servers" -p "Insira o número total de nós de mixagem: " input
num_servers="${input:-$num_servers}"

thres="2"
read -e -i "$thres" -p "Insira o número threshold de nós: " input
thres="${input:-$thres}"

session_id="ShuffleSession"
read -e -i "$session_id" -p "Insira o ID da sessão: " input
session_id="${input:-$session_id}"

election_name="ShufflerNet"
read -e -i "$election_name" -p "Insira o nome da eleição: " input
election_name="${input:-$election_name}"

curl -sS -X POST http://localhost:8080/shuffler/setup-local \
    -d "serverId=$mix_server&numServers=$num_servers&thres=$thres&sessionId=$session_id&electionName=$election_name"