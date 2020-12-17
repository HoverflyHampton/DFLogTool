# Data Flash Parser
## About  
This tool is used to merge logs in data flash format. It will sort merged log line on timestamp, automatically resolve name conflicts, and allows targeted column merging and time offsets between files. See the 'examples' section to see how to call it, or pass the -h argument for detailed help  

## Requirements
- Python 3.5+
- Pandas 1.0.5+
- Numpy 1.19.1+
- Kivy 1.11.1+

### Installing Requirements
#### Conda
For package managment, install Miniconda for python 3 from the following link : https://docs.conda.io/en/latest/miniconda.html. Once install is complete, there should be a new program called `Anaconda Prompt` - run the following commands in that prompt

```
cd <Location of Dataflash Merger Folder>
conda create --name dataflash
conda activate dataflash
```

From now on, before running the data flash parser for the first time after opening the Anaconda Prompt, make sure to call `conda activate dataflash`.

#### Numpy
Call `conda install numpy` from the Anaconda prompt

#### Pandas
Call `conda install pandas` from the Anaconda prompt

#### Kivy
Call `conda install kivy` from the Anaconda prompt
## GUI Application
To run the GUI application, call `python cli.py` from the top level folder.

## Examples
To run the command line application, cd into the log_parser directory. Then, on Linux run with `./DFParser.py`. On Windows, call with `python DFParser.py`
#### Basic Merge of Multiple files
`./DFParser.py <path_to_output_file> <path_to_main_file> -f <path_to_merge_file1> <path_to_merge_fileX>`  
#### Merge with time offset  
`./DFParser.py <path_to_output_file> <path_to_main_file> -f <path_to_merge_file> -t <int_time_offset>`  
#### Merge, ignoring tables in incoming files  
`./DFParser.py <path_to_output_file> <path_to_main_file> -f <path_to_merge_file> -d <msg_name_to_ignore>`  
#### Merge, automatically finding time synch from IPS/Bgu file
`./DFParser.py <path_to_output_file> <path_to_main_file> -a <path_to_ips_or_bgu_file> -f <path_to_merge_file>`  

## As a library
The DFParser code can be called as a library in order to manipulate dataflash logs in python. The main useful structure of the DFParser object is the tables field. `tables` is a dictionary keyed on message name containing a pandas DataFrame with all the messages of the type listed. 
