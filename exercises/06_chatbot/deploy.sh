#!/bin/bash
cd "$(dirname "$0")"
source ../../.venv/bin/activate
export ZENML_ANALYTICS_OPT_IN=false
unset KITARU_CONFIG_PATH
exec kitaru deploy chatbot.py:chatbot --tag prod --stack aws-k8s-stack --exclusive
