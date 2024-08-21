#!/bin/bash

if [ -d "build" ]; then
  rm -rf build
fi

if [ -d "dist" ]; then
  rm -rf dist
fi

flet pack src/server.py --add-data 'src/assets;.' --add-data './app.log;.' -i icons/sticks.ico -n XLM