# remove any existing backup
rm -rf {{location}}/of2030.bak
# move current version to backup
mv {{location}}/of2030 {{location}}/of2030.bak
# make new of2030 folder
mkdir {{location}}/of2030
# extract tar into folder
tar -zxf {{tarfile}} -C {{location}}/of2030 --warning=no-timestamp
# copy some build files from the backup into the new dir
cp -r {{location}}/of2030.bak/obj {{location}}/of2030/
cp {{location}}/of2030.bak/bin/of2030 {{location}}/of2030/bin/
cp {{location}}/of2030.bak/bin/of2030_debug {{location}}/of2030/bin/
cp -r {{location}}/of2030.bak/bin/libs {{location}}/of2030/bin/
