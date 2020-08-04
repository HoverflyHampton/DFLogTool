# Data Flash Parser
## About  
This tool is used to merge logs in data flash format. It will sort merged log line on timestamp, automatically resolve name conflicts, and allows targeted column merging and time offsets bnetween files. See the 'examples' section to see how to call it, or pass the -h argument for detailed help  

## Examples
On Linux, run with `./DFParser.py`. On Windows, call with `python3 DFParser.py`
#### Basic Merge of Multiple files
`./DFParser.py <path_to_output_file> <path_to_main_file> <path_to_merge_file1> <path_to_merge_fileX>`
#### Merge with time offset  
`./DFParser.py <path_to_output_file> <path_to_main_file> <path_to_merge_file> -t <int_time_offset>`
#### Merge, ignoring tables in incoming files  
`./DFParser.py <path_to_output_file> <path_to_main_file> <path_to_merge_file> -d <msg_name_to_ignore>`

## As a library
The DFParser code can be called as a library in order to manipulate dataflash logs in python. The main useful structure of the DFParser object is the tables field. `tables` is a dictionary keyed on message name containing a pandas DataFrame with all the messages of the type listed. 