# remove any existing backup
rm -rf {{location}}.bak
# move current version to backup
mv {{location}} {{location}}.bak
# make new of2030 folder
mkdir {{location}}
# extract tar into location
tar -zxf {{tarfile}} -C {{location}} --warning=no-timestamp
