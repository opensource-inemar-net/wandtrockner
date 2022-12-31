sudo sed -i '/denyinterfaces wlan0/d' /etc/dhcpcd.conf
sudo rm /etc/network/interfaces.d/wlan0
sudo sed -i 's/DAEMON_CONF/#DAEMON_CONF/g' /etc/default/hostapd
sudo rm /etc/dnsmasq.conf
sudo systemctl stop hostapd
sudo systemctl disable hostapd
sudo systemctl mask hostapd 
sudo reboot

