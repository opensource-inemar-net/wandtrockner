This repository contains a self contained IOT device based on rasperry pi.

It connects to tow devices:
 - powermeter via modbus ethernet
 - GSM/LTE module 


the service runs a webserver based on flask and a cronjob exectuted every minute that creates measurements etc.

To install do the following:

- create a new rasperry pi image with the following parameters:
    - device name is the device name, that shall be used
    - enable ssh
    - create root user with name inemar
    - enable ssh
    - enable wlan connection


- start the rasperry pi
- connect via ssh to the rasperry pi

- execute the following commands to get the rasperry pi to latest software
    sudo apt update 
    sudo apt full-upgrade -y

- execute the following commands to finish upgrade with a reboot
    sudo reboot

- execute the following commands to install the software

    cd /usr/local
    sudo mkdir wandtrockner
    sudo chown inemar:inemar wandtrockner
    git clone https://github.com/opensource-inemar-net/wandtrockner.git
    cd wandtrockner
    cd install
    ./install.sh

After that the system shall be working correctly

connect to the webinterface runnning on standard http powermeter





         


