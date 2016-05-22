# first remove log file
rm {{folder}}/bin/data/log.txt
tar -zcf {{tarfile}} -C {{folder}} -X {{folder}}/.tar_exclude .
