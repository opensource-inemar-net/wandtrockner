echo ""
echo ""
echo "*********************************"
echo "configure static eth0 address"
echo ""
sudo sed -i '/denyinterface eth0/d' /etc/dhcpcd.conf
sudo echo 'denyinterface eth0' >> /etc/dhcpcd.conf
sudo cp /usr/local/wandtrockner/install/eth0 /etc/network/interfaces.d
sudo ifdown eth0
sudo ifup eth0

