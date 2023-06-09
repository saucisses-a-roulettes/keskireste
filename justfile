#!/usr/bin/env just --justfile

default:
  just --list

test:
    black --check src
    mypy
    pytest

reformat:
    black src

setup:
    cp hooks/* .git/hooks/
    chmod +x .git/hooks/*
    poetry install

fastapi:
    uvicorn src.infrastructure.fastapi:app --reload
