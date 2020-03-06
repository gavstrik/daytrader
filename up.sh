#!/usr/bin/env bash
if [ "$#" -ne 2 ]; then
    echo "Usage: up [tag of docker image] [subdomain, e.g test if running on test.cibs.mef.sc.ku.dk]"
    exit 1
fi
if git rev-parse "$1^{tag}" >/dev/null 2>&1
then
    echo "Found tag $1"
else
    echo "Tag $1 does not exist"
    exit 1
fi
export TAG=$1
export SUBDOMAIN=$2
rancher up -d -s $2