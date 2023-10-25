#!/bin/bash

cd ./develop-helper-bot
poetry run python ./bot/__main__.py &
cd ..

cd ./server
poetry run python ./src/__main__.py &
cd ..