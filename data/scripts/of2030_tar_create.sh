# first remove log file
rm {{folder}}/bin/data/log.txt
# create compressed archive of the whole of2030 folder content
tar -zcf {{tarfile}} -C {{folder}} -X {{folder}}/.tar_exclude .
# # nice-to-have
touch {{folder}}/bin/data/log.txt
