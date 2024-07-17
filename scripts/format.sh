#!/bin/sh -e
export PREFIX=""

if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

export SOURCE_FILES="src cookbook tests"

set -x
${PREFIX}ruff check ${SOURCE_FILES} --fix --unsafe-fixes
${PREFIX}ruff format ${SOURCE_FILES}