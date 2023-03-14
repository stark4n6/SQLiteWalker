![alt text](https://github.com/stark4n6/SQLite-Walker/blob/main/SQLiteWalker.png)

# SQLite Walker
Python script to walk a folder or a zip file for SQLite Databases. It will export them to the output path as well as create a TSV formatted export file with a list of files found. The TSV includes the file name, paths from the source, and the table structure.

What sparked the project was being able to hunt SQLite database files using Eric Zimmerman's [SQLECmd](https://github.com/EricZimmerman/SQLECmd/tree/master/SQLECmd) while just producing a list of files only. In the [DFIR Museum](https://github.com/AndrewRathbun/DFIRArtifactMuseum/tree/main/Android) there are similar text file outputs that Andrew Rathbun created. Hopefully others can get good use out of this script for research purposes or for casework.

## ***DISCLAIMER*** 
The script works on Windows but may not have support on other OS's, feedback is greatly appreciated!

It has only been tested on test data, use at your own risk!

## Command Line Switches
```
usage: SQLite_Walker.py [-h] -i INPUT_PATH -o OUTPUT_PATH [-q]

options:
  -h, --help            show this help message and exit  
  -i INPUT_PATH, --input_path INPUT_PATH Input file/folder path  
  -o OUTPUT_PATH, --output_path OUTPUT_PATH Output folder path  
  -q, --quiet_mode      Turns off console path output  
```

### To-Do List
- GUI
- .TAR support
- Extract -wal / -shm
