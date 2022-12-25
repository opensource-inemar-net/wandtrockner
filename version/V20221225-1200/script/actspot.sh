#sudo chown root:root /usr/local/wandtrockner/active/active/script/root/*
sudo echo 'denyinterfaces wlan0' >> /etc/dhcpcd.conf
sudo cp /usr/local/wandtrockner/active/active/script/root/wlan0 /etc/network/interfaces.d 
sudo cp /usr/local/wandtrockner/active/active/script/root/hostapd /etc/default/hostapd
sudo cp /usr/local/wandtrockner/active/active/script/root/dnsmasq.conf /etc
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo reboot

