# create subdirectory with timestamp postfix
mkdir {{folder}}
# extract archive into created subdirectory
tar -zxf {{tarfile}} -C {{folder}} --warning=no-timestamp
# rename 'new' config file,assuming it shouldn't overwrite current config file
mv {{folder}}/config/config.yaml {{folder}}/config/config.yaml.new
# copy config from previous folder to new folder
cp ./py2030/config/config.yaml {{folder}}/config/config.yaml
# remove existing softlink (./py2030)
rm ./py2030
# create new softlink to just created subdirectory
ln -s {{folder}} py2030