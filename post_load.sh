#!/bin/bash

./database/run_sql.sh database/constrains.sql
./database/run_sql.sh database/indexes.sql
./database/run_sql.sh database/vacumme_and_analyze.sql
