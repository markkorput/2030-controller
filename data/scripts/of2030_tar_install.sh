# remove any existing backup
rm -rf {{location}}/of2030.bak
# move current version to backup
mv {{location}}/of2030 {{location}}/of2030.bak
# make new of2030 folder
mkdir {{location}}/of2030
# extract tar into folder
tar -zxf {{tarfile}} -C {{location}}/of2030 --warning=no-timestamp
# overwrite client id
echo "<of2030><client_id>{{client_id}}</client_id></of2030>" > {{location}}/of2030/bin/data/client_id.xml
# nice-to-have
touch {{location}}/of2030/bin/data/log.txt
