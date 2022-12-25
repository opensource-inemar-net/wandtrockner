sudo cp ./flask.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start flask.service
sudo systemctl enable flask.service


