echo ""
echo ""
echo "*********************************"
echo "changing now privilege port to allow running on port 80"
echo ""
sudo cp /usr/local/Wandtrockner/install/privport.conf > /etc/sysctl.d/privport.conf
sudo sysctl --system


