# create subdirectory with timestamp postfix
mkdir {{folder}}
# extract archive into created subdirectory
tar -zxf {{tarfile}} -C {{folder}} --warning=no-timestamp
# remove existing softlink (./py2030)
rm ./py2030
# create new softlink to just created subdirectory
ln -s {{folder}} py2030
