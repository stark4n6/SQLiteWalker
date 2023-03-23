import csv
import argparse
import os
import shutil
import sqlite3
import sys
import time
from zipfile import ZipFile
import zipfile

ascii_art = '''
        _______.  ______      __       __  .___________. _______        
       /       | /  __  \    |  |     |  | |           ||   ____|       
      |   (----`|  |  |  |   |  |     |  | `---|  |----`|  |__          
       \   \    |  |  |  |   |  |     |  |     |  |     |   __|         
   .----)   |   |  `--'  '--.|  `----.|  |     |  |     |  |____        
   |_______/     \_____\_____\_______||__|     |__|     |_______|                                                 
____    __    ____  ___       __       __  ___  _______ .______      
\   \  /  \  /   / /   \     |  |     |  |/  / |   ____||   _  \     
 \   \/    \/   / /  ^  \    |  |     |  '  /  |  |__   |  |_)  |    
  \            / /  /_\  \   |  |     |    <   |   __|  |      /     
   \    /\    / /  _____  \  |  `----.|  .  \  |  |____ |  |\  \----.
    \__/  \__/ /__/     \__\ |_______||__|\__\ |_______|| _| `._____|
    
                SQLiteWalker v0.0.2
                https://github.com/stark4n6/SQLiteWalker
                @KevinPagano3 | @stark4n6 | startme.stark4n6.com
                                                                     '''

def is_platform_windows():
    '''Returns True if running on Windows'''
    return os.name == 'nt'

def open_sqlite_db_readonly(path):
    '''Opens an sqlite db in read-only mode, so original db (and -wal/journal are intact)'''
    if is_platform_windows():
        if path.startswith('\\\\?\\UNC\\'): # UNC long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\?\\'):    # normal long path
            path = "%5C%5C%3F%5C" + path[4:]
        elif path.startswith('\\\\'):       # UNC path
            path = "%5C%5C%3F%5C\\UNC" + path[1:]
        else:                               # normal path
            path = "%5C%5C%3F%5C" + path
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)

def main():
    
    base = "SQLiteWalker_Out_"
    data_list = []
    error_list = []
    data_headers = ('File Name','Export Path','Tables')
    error_headers = ('File Name','Export Path','Error')
    count = 0
    error_count = 0    

    start_time = time.time()
    
    #Command line arguments
    parser = argparse.ArgumentParser(description='SQLiteWalker v0.0.2 by @KevinPagano3 | @stark4n6 | https://github.com/stark4n6/SQLiteWalker')
    parser.add_argument('-i', '--input_path', required=True, type=str, action="store", help='Input file/folder path')
    parser.add_argument('-o', '--output_path', required=True, type=str, action="store", help='Output folder path')
    parser.add_argument('-q', '--quiet_mode', required=False, action="store_true", help='Turns off console path output')
    
    args = parser.parse_args()
    
    input_path = args.input_path
    output_path = args.output_path
    quiet_mode = args.quiet_mode
    
    if args.output_path is None:
        parser.error('No OUTPUT folder path provided')
        return
    else:
        output_path = os.path.abspath(args.output_path)
    
    if output_path is None:
        parser.error('No OUTPUT folder selected. Run the program again.')
        return
    
    if input_path is None:
        parser.error('No INPUT file or folder selected. Run the program again.')
        return
    
    if not os.path.exists(input_path):
        parser.error('INPUT file/folder does not exist! Run the program again.')
        return
    
    if not os.path.exists(output_path):
        parser.error('OUTPUT folder does not exist! Run the program again.')
        return  
    
    # File system extractions can contain paths > 260 char, which causes problems
    # This fixes the problem by prefixing \\?\ on each windows path.
    if is_platform_windows():
        if input_path[1] == ':': input_path = '\\\\?\\' + input_path.replace('/', '\\')
        if output_path[1] == ':': output_path = '\\\\?\\' + output_path.replace('/', '\\')
        
        if not output_path.endswith('\\'):
            output_path = output_path + '\\'
    
    platform = is_platform_windows()
    if platform:
        splitter = '\\'
    else:
        splitter = '/'    
    #-------------------------------    
    
    print(ascii_art)
    print()
    print('Source: '+ input_path)
    print('Destination: '+ output_path)
    print('-'* (len('Source: '+ input_path)))
    
    folder, basename = os.path.split(input_path)
    
    if basename.find('.') > 0:
        if basename.endswith('.zip'):
            with zipfile.ZipFile(input_path, 'r') as my_zip:
                files = my_zip.namelist()
                output_ts = time.strftime("%Y%m%d-%H%M%S")
                out_folder = output_path + base + output_ts
                for file in files:
                    file_name = file.rsplit("/",1)
                    if file.endswith(('-shm','-wal')):
                        my_zip.extract(file,(out_folder + splitter + 'db_out'))
                        
                        new_path = out_folder + splitter + 'db_out' + file
                        if platform:
                            new_path = new_path.replace('/','\\')
                        
                        data_list.append((file_name[1], new_path[4:], ''))
                    else:
                        with my_zip.open(file) as f:
                            header = f.read(100)
                            if header.startswith(b'\x53\x51\x4c\x69\x74\x65\x20\x66\x6f\x72\x6d\x61\x74\x20\x33\x00'):
                                my_zip.extract(file,(out_folder + splitter + 'db_out'))
                                try:
                                    new_path = out_folder + splitter + 'db_out' + file
                                    if platform:
                                        new_path = new_path.replace('/','\\')                                    
                                    
                                    db_connect = sqlite3.connect(new_path)
                
                                    sql_query = """SELECT name FROM sqlite_master
                                    WHERE type='table';"""
                                
                                    cursor = db_connect.cursor()
                                    cursor.execute(sql_query)
                                    
                                    # printing all tables list
                                    tables = cursor.fetchall()
                                    tables_list = []
                                    
                                    entries = len(tables)
                                    if entries > 0:
                                        for row in tables:
                                            tables_list.append(row[0])
                                        
                                        data_list.append((file_name[1], new_path[4:], tables_list))
                                        count += 1
                                        if not quiet_mode:
                                            print('DB '+str(count) + ': ' + file)
                                    
                                except sqlite3.Error as error:
                                    if not quiet_mode:
                                        print("Failed to open the database: ", error)
                                        print(file)
                                    error_list.append((file_name[1], new_path[4:], error))
                                    error_count += 1
                                
                                finally:
                                    if db_connect:
                                        db_connect.close()
        else:
            print('File is not a .zip, please try again. Exiting......')
            sys.exit()
    
    else:
        output_ts = time.strftime("%Y%m%d-%H%M%S")
        out_folder = output_path + base + output_ts
        os.mkdir(out_folder)
        
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith(('-shm','-wal')):
                    src_file_path = os.path.join(root, file)
                    
                    dest_folder_path = os.path.join(out_folder, os.path.relpath(root, input_path))
                    dest_file_path = os.path.join(dest_folder_path, file)
                    os.makedirs(dest_folder_path, exist_ok=True)
                    
                    shutil.copy2(src_file_path, dest_file_path)
                    data_list.append((file, dest_file_path[4:], ''))
                            
                else:      
                    src_file_path = os.path.join(root, file)
                    if os.path.isfile(src_file_path):
                        if os.path.getsize(src_file_path) > 100:                      
                            with open(src_file_path,'r', encoding = "ISO-8859-1") as f:
                                header = f.read(100)
                                if header.startswith('SQLite format 3'):
                                    try:
                                        db_connect = open_sqlite_db_readonly(src_file_path)
            
                                        sql_query = """SELECT name FROM sqlite_master
                                        WHERE type='table';"""
                                    
                                        cursor = db_connect.cursor()
                                        cursor.execute(sql_query)
                                        
                                        tables = cursor.fetchall()
                                        tables_list = []
                                        
                                        for row in tables:
                                            tables_list.append(row[0])
                                        
                                        count += 1
                                        if not quiet_mode:
                                            print('DB '+str(count) + ': ' + src_file_path)
    
                                            src_file_path = os.path.join(root, file)
                                            
                                            dest_folder_path = os.path.join(out_folder, os.path.relpath(root, input_path))
                                            dest_file_path = os.path.join(dest_folder_path, file)
                                            os.makedirs(dest_folder_path, exist_ok=True)
                                            
                                            shutil.copy2(src_file_path, dest_file_path)
                                            data_list.append((file, dest_file_path[4:], tables_list))
                                        
                                    except sqlite3.Error as error:
                                        if not quiet_mode:
                                            print("Failed to execute the above query", error)
                                            print(file)
                                        error_list.append((file, dest_file_path[4:], error))
                                        error_count += 1
                                    
                                    finally:
                                        if db_connect:
                                            db_connect.close()    
                                
    with open(out_folder + splitter + 'db_list.tsv', 'w', newline='') as f_output:
        tsv_writer = csv.writer(f_output, delimiter='\t')
        tsv_writer.writerow(data_headers)
        for i in data_list:
            tsv_writer.writerow(i)
            
    if error_count > 0:
        with open(out_folder + splitter + 'error_list.tsv', 'w', newline='') as f_output:
            tsv_writer = csv.writer(f_output, delimiter='\t')
            tsv_writer.writerow(error_headers)
            for i in error_list:
                tsv_writer.writerow(i)    
        
    print()
    print('****JOB FINISHED****')
    print('Runtime: %s seconds' % (time.time() - start_time))
    print('DBs Found: ' + str(count))
    print('Error Count: ' + str(error_count))
    if error_count > 0:
        print('Check error file error_list.tsv for details')

if __name__ == '__main__':
    main()