# make new of2030 folder
mkdir {{location}}/{{folder}}
# extract tar into folder
tar -zxf {{tarfile}} -C {{location}}/{{folder}}
# remove existing symlink
rm of2030
# create symlink to new folder
ln -s {{location}}/{{folder}} of2030
