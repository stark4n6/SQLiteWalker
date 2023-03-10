# SQLite Walker
Python script to walk a folder or a zip file for SQLite Databases. It will export them to the output path as well as create a TSV formatted export file with a list of files found. The TSV includes the file name, paths from the source, and the table structure.

## Command Line Switches
```
usage: SQLite_Walker.py [-h] -i INPUT_PATH -o OUTPUT_PATH [-q]

options:
  -h, --help            show this help message and exit  
  -i INPUT_PATH, --input_path INPUT_PATH Input file/folder path  
  -o OUTPUT_PATH, --output_path OUTPUT_PATH Output folder path  
  -q, --quiet_mode      Turns off console path output  
```
