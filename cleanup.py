"""
Delete rows where the measurement is the same at the previous and next
timestamp. Assuming linearity, these can be removed without loss of
information.

Also prints some rough estimates for how much smaller the results are.

- bpm
- stress
"""

import argparse
import pandas as pd

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-c", "--column-name", type=str, help="Name of the column (e.g. bpm, stress)")
PARSER.add_argument("-d", "--dry-run", action="store_true", help="Show stats, but don't overwrite")
PARSER.add_argument("file", help="Input/Output file to compress")
ARGS = PARSER.parse_args()

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
    df.to_csv(ARGS.file, index=False)
