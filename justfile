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