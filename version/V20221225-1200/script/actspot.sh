sudo chown root:root /usr/local/wandtrockner/script/root
sudo echo 'denyinterfaces wlan0' >> /etc/dhcpcd.conf
sudo cp  /usr/local/wandtrockner/script/root/wlan0 /etc/network/interfaces.d 
sudo cp /usr/local/wandtrockner/script/root/hostapd /etc/default/hostapd
sudo cp  /usr/local/wandtrockner/script/root/dnsmasq.conf /etc
sudo reboot

