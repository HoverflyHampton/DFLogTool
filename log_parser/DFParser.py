#!/usr/bin/env python3

import argparse
import struct
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

    _unpack_formats = {
        'a': '32h',
        'b': 'b',
        'B': 'B',
        'h': 'h',
        'H': 'H',
        'i': 'i',
        'I': 'I',
        'f': 'f',
        'd': 'd',
        'n': '4s',
        'N': '16s',
        'Z': '64s',
        'c': 'h',
        'C': 'H',
        'e': 'i',
        'E': 'I',
        'L': 'i',
        'M': 'B',
        'q': 'q',
        'Q': 'Q'
    }

    def __init__(self, name, id, length, data_types, columns):
        self.name = name
        self.id = id
        self.length = length
        self.data_types = [MessageFormat._field_formats[char] for char in data_types]
        self.data_types = {columns[i]: self.data_types[i] for i in range(len(columns))}
        self.unpack_types = '=B' + ''.join([MessageFormat._unpack_formats[char] for char in data_types])
        self.columns = ['MSGNAME'] + columns

    def __str__(self):
        return "{}, {}, {}, {}, {}".format(self.name, self.id, self.length, self.unpack_types, self.columns)

    
class DFLog(object):
    def __init__(self, filename):
        self.tables = {}
        self._data = {}
        self._formats = {}
        if filename[-3:] == 'bin':
            self._read_from_bin_file(filename)
        else:
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

    def _read_from_bin_file(self, filename):
        with open(filename, 'rb') as infile:
            self._data['LINES'] = []
            for line in self._bin_splitter(infile):
                if line == b'':
                    continue
                type_id = line[0]
                # FMT handle
                if type_id == 128:
                    self._handle_bin_fmt(line)
                self._data['LINES'].append(line)
        current = self._data['LINES'][0]        
        for line in self._data['LINES'][1:]:
            if line[0] in self._formats and len(current) >= self._formats[current[0]].length-2:
                self._add_bin_row(current[0], current)
                current = line
            else:
                current = current + b'\xA3\x95' + line
        self._data.pop('LINES')
        if len(current) >= self._formats[current[0]].length-2:
            self._add_bin_row(current[0], current)
        self._format_bin_tables()

    def _handle_bin_fmt(self, line):
        try:
            (__, fmt_type, fmt_len, name, fmt_str, labels) = struct.unpack("BBB4s16s64s", line[:87])
            name=name.decode('ascii').strip('\x00')
            fmt_str = fmt_str.decode('ascii').strip('\x00')
            labels = labels.decode('ascii').strip('\x00').split(',')
            self._formats[fmt_type] = MessageFormat(name, fmt_type, fmt_len, fmt_str, labels)
        except struct.error:
            print("Error: Invalid Format Line")
            print(line)

    def _bin_splitter(self, filehandle):
        marker = b'\xA3\x95'
        blocksize = 4096
        current = b''
        result = b''
        for block in iter(lambda: filehandle.read(blocksize), b''):
            current += block
            while True:
                markerpos = current.find(marker)
                if markerpos == -1:
                    break
                result = current[:markerpos]
                current = current[markerpos + len(marker):]
                yield result
        yield current

    def _add_bin_row(self, type_id, data):
        if not type_id in self._data:
            self._data[type_id] = []
        self._data[type_id].append(data)

    def _format_bin_tables(self):
        for type_id in self._data:
            fmt = self._formats[type_id]
            data = [struct.unpack(fmt.unpack_types, row[:fmt.length-2])[:len(fmt.columns)]
                        for row in self._data[type_id]]

            self.tables[fmt.name] = pd.DataFrame(data, columns=fmt.columns)
            self.tables[fmt.name]['MSGNAME'] = fmt.name
            for column in self.tables[fmt.name].columns:
                if type(self.tables[fmt.name][column].iloc[0]) == bytes:
                    self.tables[fmt.name][column] = self.tables[fmt.name][column].apply(lambda x: x.decode('ascii').strip('\x00'))

    def _add_row(self, name, data):
        """Add a new row of data to the appropriate table.

        Args:
            name (str): The name of the table to add
            data (list<str>): the values to insert into the table
        """

        if not name in self._data:
            self._data[name] = []
        if name == 'FMT':
            data = data[:4] + [",".join(data[4:])]
        self._data[name].append([name] + data)

    def _format_tables(self):
        """Creates the FMT dataframe, then uses that dataframe to format the dictionaries
        """
        np_fmt = np.array(self._data['FMT'])
        fmt_names = np_fmt[:, 3]
        fmt_ids = np_fmt[:, 2]
        fmt_lens = np_fmt[:, 1]
        fmt_data_types = np_fmt[:, 4]
        fmt_cols = np_fmt[:, 5]
        self._formats = {fmt_names[i]: MessageFormat(fmt_names[i], fmt_ids[i], 
                                                     fmt_lens[i], fmt_data_types[i],
                                                     fmt_cols[i].split(','))
                         for i in range(len(fmt_names))}
        
        # Create DataFrames for each message using format dictionary
        for name in self._data:
            data  = self._data[name]
            fmt = self._formats[name]
            col_num = len(fmt.columns)-1
            data = [row[:col_num] + [", ".join(row[col_num:])] for row in data]
            self.tables[name] = pd.DataFrame(data, columns=fmt.columns)
            

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

        with open(filename, 'w') as __:
            # Clear out the file
            pass    
        with open(filename, 'a') as outfile:
            # First, write the format messages
            fmt_np = self.tables['FMT'].to_numpy()
            np.savetxt(outfile, fmt_np, fmt='%s', delimiter=',', newline='\n')
            
            # Write the rest of the log, sorted by timestamp
            numpy_msgs = None
            for table in self.tables:
                if table == 'FMT':
                    continue
                temp_array = self.tables[table].to_numpy()
                temp_array = np.hstack([temp_array[:, :1], 
                                        np.reshape([int(float(val)) for val in temp_array[:, 1]], 
                                                   (len(temp_array), 1)),
                                        np.reshape([", ".join([str(x) 
                                                         for x in row]) 
                                                    for row in temp_array[:, 2:]],
                                                    (len(temp_array), 1))])
                if numpy_msgs is None:
                    numpy_msgs = temp_array
                else:
                    numpy_msgs = np.vstack((numpy_msgs, temp_array))
            numpy_msgs = numpy_msgs[numpy_msgs[:, 1].astype(float).argsort()]
            np.savetxt(outfile, numpy_msgs, fmt='%s', delimiter=', ', newline='\n')

    def drop_empty(self):
        """ Drop all tables that have no entries, and removes thier format message
        """        
        drop_tables = []
        for table in self.tables:
            if self.tables[table].empty:
                drop_tables.append(table)
        for val in drop_tables:
            self.tables.pop(val)
            drop_idx = self.tables['FMT'][self.tables['FMT']['Type'] == val].index
            self.tables['FMT'].drop(drop_idx, inplace=True)

    def merge(self, other, drop_tables=None, time_shift=0):
        """Merges a DFParser object into this object. Has side effects on other

        Args:
            other (DFParser): The log data to add
            drop_tables (list<str>, optional) : Names of tables to not include in the merge. Defaults to None
        """        
        
        #drop unused tables in other
        other.drop_empty()
        
        # find collisions
        format_table_names = {'FMT': 'Name',
                              'UNIT': 'Id', 'MULT': 'Id', 'FMTU': 'FmtType'}
        merge_names = list(other.tables.keys())
        if drop_tables is None:
            drop_tables = []
        merge_names = [x for x in merge_names if x not in drop_tables and x not in format_table_names]
        
        collisions = [x for x in merge_names if x in self.tables ]
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
    
    def find_offset(self, other):
        # Check if self is a craft log, and other has ISP data
        if 'RCOU' not in self.tables and 'IPS' not in other.tables:
            return 0 # Can't find an offset, return no offset

        ips_launch = other.tables['IPS'][other.tables['IPS']['mA'].astype(int) > 600].iloc[0]
        craft_launch = self.tables['RCOU'][self.tables['RCOU']['C1'].astype(int) > 1500].iloc[0]
        us_offset = int(craft_launch['TimeUS']) - int(ips_launch['TimeUS'])
        return us_offset

if __name__ == "__main__":

    # Takes a list of files and a list of tables to drop from incoming files
    parser = argparse.ArgumentParser()
    parser.add_argument("output", help="The new log file to output into")
    parser.add_argument("base", help="The primary file to merge into")
    parser.add_argument("-f", "--files", help="Paths of files to merge", nargs="+")
    parser.add_argument('-d', '--drop', help='The names of fields to drop from incoming files', nargs='*')
    parser.add_argument('-t', '--time_shift', help='Number of milliseconds to shift incoming files by', type=int, default=0)
    parser.add_argument('-a', '--auto_shift', help='The name of a file to merge with automatic time shifting')
    args = parser.parse_args()

    
    log = DFLog(args.base)
    ts = args.time_shift
    if args.auto_shift is not None:
        ips_log = DFLog(args.auto_shift)
        ts += log.find_offset(ips_log)
        log.merge(ips_log, drop_tables=args.drop, time_shift=ts)
    if args.files is not None:
        for f in args.files:
            log.merge(DFLog(f), drop_tables=args.drop, time_shift=ts)
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
