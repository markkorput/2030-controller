# remove any existing backup
rm {{offolder}}/src.bak.tar.gz
# make new backup
tar -zcf {{offolder}}/src.bak.tar.gz -C {{offolder}} src
# remove current src folder content
rm {{offolder}}/src/*
# extract tar into src folder
tar -zxf {{tarfile}} -C {{offolder}}/src --warning=no-timestamp
