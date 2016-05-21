# first remove log file
rm {{offolder}}/bin/data/log.txt
tar -zcf {{tarfile}} -C {{offolder}} -X {{offolder}}/.tar_exclude .
