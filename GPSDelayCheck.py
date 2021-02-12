#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os
import argparse
from log_parser.DFParser import *

def main(file_list):
    gps_meta = []

    for filename in file_list:
        log = DFLog(filename)

        # Plan - get first three messages
        # Get max value of GPS1 delta
        firmware = log.tables["MSG"]["Message"].iloc[0]
        os = log.tables["MSG"]["Message"].iloc[1]
        hardware = log.tables["MSG"]["Message"].iloc[2]

        max_delay = log.tables['GPA']['Delta'].max()

        gps_meta.append([firmware, os, hardware, max_delay])

    gps_meta_df = pd.DataFrame(data=gps_meta, columns=["firmware", "os", "hardware", "max_delay"])
    return gps_meta_df
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="The new log file to output into")
    parser.add_argument("input_folder", help="The folder containing log files")
    args = parser.parse_args()
    folder = args.input_folder
    file_list = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".bin")]
    df = main(file_list)
    df.to_csv(args.output, index=False)