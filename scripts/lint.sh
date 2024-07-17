#!/bin/sh -e
export PREFIX=""

if [ -d '.venv' ] ; then
    export PREFIX=".venv/bin/"
fi
export SOURCE_FILES="src cookbook tests"
set -x

${PREFIX}mypy ${SOURCE_FILES}
${PREFIX}pyright ${SOURCE_FILES}
${PREFIX}ruff check ${SOURCE_FILES}
