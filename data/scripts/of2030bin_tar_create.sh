# make temp folder
rm -rf {{offolder}}/bin/bintmp
mkdir {{offolder}}/bin/bintmp
# copy bin files to tmp folder
cp {{offolder}}/bin/of2030* {{offolder}}/bin/bintmp
# create compressed archive of the whole of2030 folder content
tar -zcf {{tarfile}} -C {{offolder}}/bin/bintmp .
# # nice-to-have
rm -rf {{offolder}}/bin/bintmp