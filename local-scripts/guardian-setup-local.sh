#!/bin/bash

# Persistir variaveis recebidas em arquivo para uso posterior!!

echo "Insira o número do Nó Guardião local:"
read mix_server

num_servers="3"
read -e -i "$num_servers" -p "Insira o número total de nós guardiões: " input
num_servers="${input:-$num_servers}"

thres="2"
read -e -i "$thres" -p "Insira o número threshold de nós: " input
thres="${input:-$thres}"

session_id="GuardianSession"
read -e -i "$session_id" -p "Insira o ID da sessão: " input
session_id="${input:-$session_id}"

election_name="Guardian_Election"
read -e -i "$election_name" -p "Insira o nome da eleição: " input
election_name="${input:-$election_name}"

central_ip="127.0.0.1"
read -e -i "$central_ip" -p "Insira o ip da máquina central (front end e servidor flask): " input
central_ip="${input:-$central_ip}"

curl -sS -X POST http://localhost:8080/guardian/setup-local \
    -d "serverId=$mix_server&numServers=$num_servers&thres=$thres&sessionId=$session_id&electionName=$election_name&centralIp=$central_ip"

# curl ... URL endpoint flask para enviar /files/protInfo0x.xml