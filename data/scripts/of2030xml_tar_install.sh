# make temporary folder
mkdir {{offolder}}/bin/data/xmltmp
# copy all xml files into the temp folder
cp {{offolder}}/bin/data/*.xml {{folder}}/bin/data/xmltmp/
# create tar zip from temp folder content
tar -zcf {{offolder}}/bin/data/xml.tar.gz -C {{offolder}}/bin/data/xmltmp .
# remove temp folder folder
rm -rf {{offolder}}/bin/data/xmltmp
# remove xmls
rm {{offolder}}/bin/data/*.xml
# extract new xmls
tar -zxf {{tarfile}} -C {{offolder}}/bin/data
