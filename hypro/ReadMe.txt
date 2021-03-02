This folder contains modified version of HyspexPro for CHTC application. Following aspects have been modified:
1. All the plotting functions have been commented.
2. Images are stored in integer instead of float to cutdown the size

Steps:
1. Run prepare_CHTC_files.py to generate DEM and ATLUT for each flightline. (Part1 to Part3 in original HyspexPro.py)
2. Zip the output files(one tar ball for each flightline): Archive_CHTC_files.py. (Note:this script uses 7zip since tar command is not available on windows server. However, if run on windows 10 or unix machines, using tar command will be easier)
3. upload the original DN image + the tar ball to gluster. Prepare .dag, .sub file for the CHTC. 