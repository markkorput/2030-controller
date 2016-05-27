# remove any existing backup
rm -rf {{location}}/_raspi.bak
# move current version to backup
mv {{location}}/_raspi {{location}}/_raspi.bak
# make new of2030 folder
mkdir {{location}}/_raspi
# extract tar into location
tar -zxf {{tarfile}} -C {{location}}/_raspi --warning=no-timestamp
