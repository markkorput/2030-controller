# remove any existing backup
rm -rf {{offolder}}/bin/bin.bak
mkdir {{offolder}}/bin/bin.bak
# move current version to backup
mv {{offolder}}/bin/of2030* {{offolder}}/bin/bin.bak/
# extract tar into folder
tar -zxf {{tarfile}} -C {{offolder}}/bin --warning=no-timestamp