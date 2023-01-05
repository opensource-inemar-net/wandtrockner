date
echo "create bootreport data"
touch /usr/local/wandtrockner/messung/sms/bootreport.txt
date
echo "sleep no 30secs"
sleep 30
date
echo "Restart now dnsmasq"
sudo systemctl restart dnsmasq
echo "Finished"
date


