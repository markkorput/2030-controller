# make temporary folder
mkdir {{folder}}/bin/data/xmltmp
# copy all xml files into the temp folder
cp {{folder}}/bin/data/*.xml {{folder}}/bin/data/xmltmp/
# create tar zip from temp folder content
tar -zcvf {{tarfile}} -C {{folder}}/bin/data/xmltmp .
# remove temp folder
rm -rf {{folder}}/bin/data/xmltmp
