"""
Delete rows where the measurement is the same at the previous and next
timestamp. Assuming linearity, these can be removed without loss of
information.

Also prints some rough estimates for how much smaller the results are.

- bpm
- stress
- level
- spo2

---

Currently this operates on one file at a time, so here's a shell
script for running it on multiple files:

```
#!/usr/bin/env bash

for file in data/stress/*.csv; do
    python cleanup.py -c stress $file
done

for file in data/heart_rate/*.csv; do
    python cleanup.py -c bpm $file
done

for file in data/sleep/*.csv; do
    python cleanup.py -c level $file
done

for file in data/blood_oxygenation/*.csv; do
    python cleanup.py -c spo2 $file
done
```
"""

import argparse
import pandas as pd
import logging
import json

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-c", "--column-name", type=str, help="Name of the column (e.g. bpm, stress)")
PARSER.add_argument("-d", "--dry-run", action="store_true", help="Show stats, but don't overwrite")
PARSER.add_argument("file", help="Input/Output file to compress")
ARGS = PARSER.parse_args()

logging.basicConfig(filename='cleanup.log', level=logging.INFO, format='%(message)s')

df = pd.read_csv(ARGS.file)
column = ARGS.column_name

n_rows_orig, _ = df.shape

df = df.loc[(df[column].shift(1) != df[column]) | (df[column] != df[column].shift(-1))]

n_rows_new, _ = df.shape

orig_str = "{:,}".format(n_rows_orig).rjust(15)
new_str = "{:,}".format(n_rows_new).rjust(15)

print(f"# rows original: {orig_str}")
print(f"# rows updated:  {new_str}")
print("    {0}x smaller".format(round(n_rows_orig / n_rows_new, 2)))

if not ARGS.dry_run:
    print("Writing to csv")

    logging.info(f"{json.dumps([ARGS.file, n_rows_orig, n_rows_new])}")

    df.to_csv(ARGS.file, index=False)
