#!/bin/bash

REPODIRECTORY="$(dirname $(dirname $(realpath -s $0)))"
SOURCEDIRECTORY=${REPODIRECTORY}/source

python3 -m pylint ${SOURCEDIRECTORY}

