echo "changing now privilege port to allow running on port 80"
sudo cp ./privport.conf > /etc/sysctl.d/privport.conf
sudo sysctl --system


