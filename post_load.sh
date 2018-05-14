#!/bin/bash

# This file is following after batach processing to built indexes and vacumming

./database/run_sql.sh database/constrains.sql
./database/run_sql.sh database/indexes.sql
./database/run_sql.sh database/vacumme_and_analyze.sql
