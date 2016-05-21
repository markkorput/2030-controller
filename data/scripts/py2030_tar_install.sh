# BEFORE executing this script; make sure the file py2030.tar.gz is in the current directory
tarfile=py2030.tar.gz
subdir=py2030-$(date +%Y%m%d_%H%M%S)
# create subdirectory with timestamp postfix
mkdir $subdir
# extract archive into created subdirectory
tar -zxvf $tarfile -C $subdir
# remove existing softlink (./py2030)
rm ./py2030
# create new softlink to just created subdirectory
ln -s $subdir py2030
