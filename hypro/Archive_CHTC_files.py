"""
Archive the CHTC_files into individual tar balls.
example: python Archive_CHTC_files.py -id Z:\townsenduser-rw\HyspexPro\Output\Cheesehead\CHEESE_20190806_P2 -od Z:\townsenduser-rw\HyspexPro\Output\Cheesehead
"""

import os,glob,argparse,subprocess


def main():
    parser = argparse.ArgumentParser(description = "Archive folder to tar ball")
    parser.add_argument("-id", help="Input directory",required=True, type = str)
    parser.add_argument("-od", help="Output directory for all resulting products", required=True, type = str)
    args = parser.parse_args()

    # Get all subdirectories inside the input directory
    sub_dir_ls = glob.glob(args.id + '/*/')

    for sub in sub_dir_ls:
        filename =  os.path.basename(os.path.dirname(sub))
        if filename == 'bash': continue
        # construct the zip command:
        CMD = r'"C:/Program Files/7-Zip/7z.exe"' + ' a '+ args.od + '/'+filename + '.tar ' + sub
        p = subprocess.Popen(CMD,stdout=subprocess.PIPE,shell = True)
        #(output,err) = p.communicate()
        p_satus = p.wait()
        print('zipped folder: ' + sub)
        

if __name__== "__main__":
    main() 

