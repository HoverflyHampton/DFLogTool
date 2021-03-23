import pandas as pd
import numpy as np
import argparse

from log_parser.DFParser import *

def logToCSV(filename):
    log = DFLog(filename)
    gpsTable = 'GPSB'
    if 'GPSB' not in log.tables:
        gpsTable = 'GPS'

    df = log.tables[gpsTable][['TimeUS', 'Lat', 'Lng', 'Alt']].copy()
    df['Roll'] = 0
    df['Pitch'] = 0
    df['Yaw'] = 0
    df2 = log.tables['ATT'][['TimeUS', 'Roll', 'Pitch', 'Yaw']].copy()
    df = insertRPY(df, df2)
    df['TimeUS'] -= df.loc[0, 'TimeUS']
    df['TimeUS'] /= 1E6
    df['Lat'] /= 1E7
    df['Lng'] /= 1E7
    df['Alt'] /= 1E2
    df['Roll'] /= 1E3
    df['Pitch'] /= 1E3
    df['Yaw'] /= 1E3

    # df = df.join(df2, on='TimeUS', how='outer')
    return df

def insertRPY(base_df, rpy_df):
    curr_rpy_idx = 0
    max_idx = max(base_df.index.values)
    for idx in base_df.index.values:
        while (curr_rpy_idx in rpy_df.index.values) and (
                base_df.iloc[idx]['TimeUS'] > rpy_df.iloc[curr_rpy_idx]['TimeUS']):
            curr_rpy_idx += 1

        base_df.loc[idx, 'Roll'] = rpy_df.loc[curr_rpy_idx, 'Roll']
        base_df.loc[idx, 'Pitch'] = rpy_df.loc[curr_rpy_idx, 'Pitch']
        base_df.loc[idx, 'Yaw'] = rpy_df.loc[curr_rpy_idx, 'Yaw']
        # if idx%100 == 0:
        #     print("{}/{}".format(idx, max_idx))
    return base_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputFile", help="The log file to create a csv of")
    args = parser.parse_args()
    infile = args.inputFile
    df = logToCSV(infile)
    df.to_csv(infile.split('.')[0]+'.csv', index=False)