#!/usr/bin/env bash

# Start Grakn.ai server
grakn server start

# Create keyspace; define schema
grakn console --keyspace office_ally_patients --file database/patient-matching-schema.gql

# Import data
python3 importer/import-patient-records.py 'office_ally_patients' 'sample-data/Patient Matching Data.csv'
