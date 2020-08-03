#!/usr/bin/env python3

import argparse
import numpy as np
import pandas as pd



class MessageFormat(object):
    _field_formats = {
        'a': str,
        'b': int,
        'B': int,
        'h': int,
        'H': int,
        'i': int,
        'I': int,
        'f': float,
        'd': float,
        'n': str,
        'N': str,
        'Z': str,
        'c': float,
        'C': float,
        'e': float,
        'E': float,
        'L': float,
        'M': str,
        'q': int,
        'Q': int
    }

    def __init__(self, name, id, data_types, columns):
        self.name = name
        self.id = id
        self.data_types = [MessageFormat._field_formats[char] for char in data_types]
        self.data_types = {columns[i]: self.data_types[i] for i in range(len(columns))}
        self.columns = columns

    def __str__(self):
        return "{}, {}, {}, {}".format(self.name, self.id, self.data_types, self.columns)

    
class DFLog(object):
    def __init__(self, filename):
        self.tables = {}
        self._data = {}
        self._formats = {}
        self._read_from_file(filename)

    
    def _read_from_file(self, filename):
        """Reads a log file into the datastructure

        Args:
            filename (str): The location of the input log`
        """
        with open(filename, 'r') as infile:
            for line in infile:
                data = [val.strip() for val in line.split(',')]
                if data[0] == 'FMT':
                    self.tables[data[3]] = pd.DataFrame(columns=data[5:])
                self._add_row(data[0], data[1:])
            self._format_tables()
        
    
    def _add_row(self, name, data):
        """Add a new row of data to the appropriate table. If the table does not exist, 
           create it with temporary column names.

        Args:
            name (str): The name of the table to add
            data (list<str>): the values to insert into the table
        """

        if not name in self._data:
            self._data[name] = []
        # TODO: Add dictionary where each entry is the column name: value  to self.data[name]
        if name == 'FMT':
            data = data[:4] + [",".join(data[4:])]
        self._data[name].append(data)

    def _format_tables(self):
        """Creates the FMT dataframe, then uses that dataframe to format the dictionaries
        """
        np_fmt = np.array(self._data['FMT'])
        fmt_names = np_fmt[:, 2]
        fmt_ids = np_fmt[:, 1]
        fmt_data_types = np_fmt[:, 3]
        fmt_cols = np_fmt[:, 4]
        self._formats = {fmt_names[i]: MessageFormat(fmt_names[i], fmt_ids[i],
                                                     fmt_data_types[i], 
                                                     fmt_cols[i].split(','))
                         for i in range(len(fmt_names))}
        
        # Create DataFrames for each message using format dictionary
        for name in self._data:
            data  = self._data[name]
            format = self._formats[name]
            col_num = len(format.columns)-1
            data = [row[:col_num] + [", ".join(row[col_num:])] for row in data]
            self.tables[name] = pd.DataFrame(data, columns=format.columns)
            # self.tables[name] = self.tables[name].astype(format.data_types)

    def _row_to_string(self, name, row):
        """Creates a dataflash string from a row of a table

        Args:
            name (str): The name of the table to create the string from
            row (int): The location in the table to create the string

        Returns:
            str: A string in the dataflash format with the values of the row
        """        
        return name+", " + ", ".join(map(str, self.tables[name].iloc[row])) + '\n'

    def output_log(self, filename, timestamp='TimeUS'):
        """Outputs the stored tables as a dataflash log

        Args:
            filename (str): The location to save the file
            timestamp (str, optional): The column sort messages on. Defaults to 'TimeUS'.
        """        
        with open(filename, 'w') as outfile:
            # First, write the format messages
            self.tables['FMT'].to_csv('fmt_table.csv')
            for fmt_line in [self._row_to_string('FMT', i) for i in 
                             range(len(self.tables['FMT']))]:
                outfile.write(fmt_line)
            
            # Basic Idea for printing messages in order:
            # Create dictionary with name: row_index for each name
            # Create unifed array of tuble (timestamp, name) for all messages
            # Sort unified array
            # Pop off array, get message row_index for name, increment row_index of name
            row_indexes = {name: 0 for name in self.tables}

            sortable_array = np.vstack([[(self.tables[name][timestamp].iloc[i], name) 
                                          for i in range(len(self.tables[name]))]
                                        for name in self.tables if name != 'FMT' and not self.tables[name].empty])
            sortable_array = sortable_array[np.argsort(sortable_array[:, 0])]
            for message in sortable_array:
                outfile.write(self._row_to_string(message[1], row_indexes[message[1]]))
                row_indexes[message[1]] += 1

    def merge(self, other, drop_tables=None, time_shift=0):
        """Merges a DFParser object into this object. Has side effects on other

        Args:
            other (DFParser): The log data to add
            drop_tables (list<str>, optional) : Names of tables to not include in the merge. Defaults to None
        """        
        # find collisions
        format_table_names = {'FMT': 'Name',
                              'UNIT': 'Id', 'MULT': 'Id', 'FMTU': 'FmtType'}
        merge_names = list(other.tables.keys())
        if drop_tables is None:
            drop_tables = []
        merge_names = [x for x in merge_names if x not in drop_tables and x not in format_table_names]
        
        collisions = [x for x in merge_names if x in self.tables ]
        print(collisions)
        if collisions:
            # We need to rename all of the colliding columns in other, 
            # and change the FMT tables names with new column names
           
            rename_chars = ['X', 'Z', 'Q', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            new_names = collisions
            for char in rename_chars:
                new_names = [char + '{:>4}'.format(name)[1:].strip() for name in collisions]
                # Check for collisions again - empty list means no collisions
                if not [x for x in new_names if x in self.tables]:
                    break
            rename_char = new_names[0][0]
            # Rename table keys in other
            for idx, name in enumerate(collisions):
                other.tables[new_names[idx]] = other.tables.pop(name)
            #Rename the messages in 'FMT'
            fmt_mask = other.tables['FMT']['Name'].isin(collisions)
            other.tables['FMT'].loc[fmt_mask, 'Name'] = \
                other.tables['FMT'].loc[fmt_mask, 'Name'].apply(
                                                        lambda x: \
                                                        rename_char + \
                                                        '{:>4}'.format(x)[1:].strip())
        
        
        # We append the FMT, UNIT, MULT, and FMTU tables
        # We then drop duplicate unit, mult and fmtu messages (check on type fields)
        for __, (name, field) in enumerate(format_table_names.items()):
            if name in other.tables:
                self.tables[name] = pd.concat([self.tables[name], other.tables[name]],
                                          ignore_index=True)
            self.tables[name] = self.tables[name].drop_duplicates(subset=[field])
        
        # and insert the new message dataframes into tables
        for name in [x for x in other.tables if x not in drop_tables and x not in format_table_names]:
            other.tables[name]['TimeUS'] = other.tables[name]['TimeUS'].astype(int) + time_shift
            self.tables[name] = other.tables[name]
    

    

if __name__ == "__main__":

    # Takes a list of files and a list of tables to drop from incoming files
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="The new log file to output into")
    parser.add_argument("base", help="The primary file to merge into")
    parser.add_argument("files", help="Paths of files to merge", nargs="+")
    parser.add_argument('-d', '--drop', help='The names of fields to drop from incoming files', nargs='*')
    parser.add_argument('-t', '--time_shift', help='Number of milliseconds to shift incoming files by', type=int)
    args = parser.parse_args()

    
    log = DFLog(args.base)
    for f in args.files:
        log.merge(DFLog(f), drop_tables=args.drop, time_shift=args.time_shift)
    log.output_log(args.output)



'''
Format characters in the format string for binary log messages
  a   : int16_t[32]
  b   : int8_t
  B   : uint8_t
  h   : int16_t
  H   : uint16_t
  i   : int32_t
  I   : uint32_t
  f   : float
  d   : double
  n   : char[4]
  N   : char[16]
  Z   : char[64]
  c   : int16_t * 100
  C   : uint16_t * 100
  e   : int32_t * 100
  E   : uint32_t * 100
  L   : int32_t latitude/longitude
  M   : uint8_t flight mode
  q   : int64_t
  Q   : uint64_t
'''
