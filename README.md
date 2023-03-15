![alt text](https://github.com/stark4n6/SQLite-Walker/blob/main/Artwork/SQLiteWalker.png)

# SQLite Walker
SQLite Walker is a python script to walk a folder or a zip file looking for SQLite databases. If it finds any it will query the table structure and export them to the output path and create a TSV formatted export file with a list of files found. The TSV includes the file name, paths from the source, and the table structure. Hopefully others can get good use out of this script for research purposes or for quick triage during casework.

Blog link: [https://www.stark4n6.com/2023/03/introducing-sqlitewalker.html](https://www.stark4n6.com/2023/03/introducing-sqlitewalker.html)

## ***DISCLAIMER*** 
The script works on Windows but may not have support on other OS's, feedback is greatly appreciated!

The script has only been run on test data, use at your own risk!

## Command Line Switches
```
usage: SQLiteWalker.py [-h] -i INPUT_PATH -o OUTPUT_PATH [-q]

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

## Acknowledgements
What sparked the project was being able to hunt SQLite database files using Eric Zimmerman's [SQLECmd](https://github.com/EricZimmerman/SQLECmd/tree/master/SQLECmd) while just producing a list of files only (no map parsing). In the [DFIR Museum](https://github.com/AndrewRathbun/DFIRArtifactMuseum/tree/main/Android) there are similar text file outputs that Andrew Rathbun created which gave me the idea for this script. I want to thank Alexis Brignoni for small snippets of code pulled from ALEAPP.
