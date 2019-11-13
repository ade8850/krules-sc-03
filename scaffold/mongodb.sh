#!/usr/bin/env bash

kubectl port-forward --namespace kubeapps svc/krul-mongodb-01 27017:27017