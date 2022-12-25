#sudo chown root:root /usr/local/wandtrockner/active/active/script/root/*
sed -i '/ssid/d' /usr/local/wandtrockner/active/active/script/root/hostapd.conf
echo -n "ssid=";cat /usr/local/wandtrockner/config/device.txt >> /usr/local/wandtrockner/active/active/script/root/hostapd.conf
sudo echo 'denyinterfaces wlan0' >> /etc/dhcpcd.conf
sudo cp /usr/local/wandtrockner/active/active/script/root/wlan0 /etc/network/interfaces.d 
sudo cp /usr/local/wandtrockner/active/active/script/root/hostapd /etc/default/hostapd
sudo rm /etc/hostapd/hostapd.conf
sudo cp /usr/local/wandtrockner/active/active/script/root/hostapd.conf /etc/hostapd
sudo cp /usr/local/wandtrockner/active/active/script/root/dnsmasq.conf /etc
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo reboot

