# remove any existing backup
rm -rf {{location}}/of2030.bak
# move current version to backup
mv {{location}}/of2030 {{location}}/of2030.bak
# make new of2030 folder
mkdir {{location}}/of2030
# extract tar into folder
tar -zxf {{tarfile}} -C {{location}}/of2030
# # remove existing symlink
# rm of2030
# # create symlink to new folder
# ln -s {{location}}/of2030
