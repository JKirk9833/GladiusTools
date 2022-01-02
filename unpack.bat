python3 ./gladius_tools.py unpack_iso
if NOT exist gladiusMODDED/ python3 ./gladius_tools.py unpack_iso --file_path GladiusVANILLA.iso --output_dir gladiusMODDED/ --file_list gladiusMODDED_FileList.txt
pause