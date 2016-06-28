rm -rf /home/pi/openFrameworks/apps/of2030/of2030/bin/data/vids/_raspi.bak
mv /home/pi/openFrameworks/apps/of2030/of2030/bin/data/vids/_raspi /home/pi/openFrameworks/apps/of2030/of2030/bin/data/vids/_raspi.bak
mkdir /home/pi/openFrameworks/apps/of2030/of2030/bin/data/vids/_raspi
tar -zxf vids.tar.gz -C /home/pi/openFrameworks/apps/of2030/of2030/bin/data/vids/_raspi --warning=no-timestamp