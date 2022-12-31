echo ""
echo ""
echo "*********************************"
echo "installing now the flask service"
echo ""
sudo cp ./flask.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start flask.service
sudo systemctl enable flask.service
echo "installing now the boot service"
sudo cp ./bootreport.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start bootreport.service
sudo systemctl enable bootreport.service

