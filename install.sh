#!/bin/bash

cd ./develop-helper-bot
poetry install
cd ..

cd ./server
poetry install
cd ..