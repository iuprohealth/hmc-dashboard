# Copyright 2022 Alexander L. Hayes

"""
The 'data/' directory contains slow-changing information, so it's
convenient to generate some metadata about the files in it.
"""

from collections import defaultdict
import os
from pathlib import Path

from tqdm import tqdm
import pandas as pd


def slug_string(input_string):
    if len(input_string) > 15:
        return input_string[:7]
    return input_string


if __name__ == "__main__":

    # The "data_types" are defined as the set of folders in the "data" directory.
    data_types = sorted(os.listdir("data"))

    users = defaultdict(lambda: [0] * len(data_types))

    for dir in os.listdir("data"):

        path = Path("data").joinpath(dir)

        for file in tqdm(os.listdir(path)):
            with open(path.joinpath(file), "r") as fh:
                lines = len(fh.read().splitlines()) - 1

            users[file.replace(".csv", "")][data_types.index(dir)] = lines

    df = pd.DataFrame(
        [(user, slug_string(user), *users[user]) for user in users],
        columns=['user_full', 'user'] + data_types,
    )

    print("Writing to user_metadata.csv")
    df.to_csv("user_metadata.csv", index=None)
