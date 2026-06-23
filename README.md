<p align="center"><img src=(https://github.com/stark4n6/SQLiteWalker/blob/main/logo.png) alt="SQLiteWalker" width="300" height="300"></p>

# SQLiteWalker
SQLiteWalker is a python script to walk a folder or archive file looking for SQLite databases. If it finds any it will query the table structure and export them to the output path and create a TSV and SQLite formatted export file with a list of files found. The TSV includes the file name, data type, paths from the source, and the table structure. Hopefully others can get good use out of this script for research purposes or for quick triage during casework.

Blog link: [https://www.stark4n6.com/2023/03/introducing-sqlitewalker.html](https://www.stark4n6.com/2023/03/introducing-sqlitewalker.html)

v1 blog link: []()

## ***DISCLAIMER*** 
The script works on Windows but may not have support on other OS's, feedback is greatly appreciated!

The script has only been run on test data, use at your own risk!

## Command Line Switches
```
usage: SQLiteWalker.py [-i SOURCE] [-o OUTPUT] [-t {folder,archive}] [-h]

SQLiteWalker 1.0.0 | https://github.com/stark4n6/SQLiteWalker | https://startme.stark4n6.com

options:
  -i SOURCE, --source SOURCE
                        Path to input file or directory to scan.
  -o OUTPUT, --output OUTPUT
                        Path to base output directory where compilation directory is written.
  -t {folder,archive}, --type {folder,archive}
                        Specify source target mapping context.
  -h, --help            Show this help message and exit. 
```

## Acknowledgements
What sparked the project was being able to hunt SQLite database files using Eric Zimmerman's [SQLECmd](https://github.com/EricZimmerman/SQLECmd/tree/master/SQLECmd) while just producing a list of files only (no map parsing). In the [DFIR Museum](https://github.com/AndrewRathbun/DFIRArtifactMuseum/tree/main/Android) there are similar text file outputs that Andrew Rathbun created which gave me the idea for this script. I want to thank Alexis Brignoni for small snippets of code pulled from ALEAPP.

A big thank you to my colleague [Miguel Palma] (https://www.linkedin.com/in/miguel-angelo-palma)/[@Mipa97](https://github.com/Mipa97) for the v1 rework including the GUI updates.
