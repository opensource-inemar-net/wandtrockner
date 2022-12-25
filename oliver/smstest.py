#!/usr/bin/env python

"""
Demo: Send Simple SMS Demo
Simple demo to send sms via gsmmodem package
"""
from __future__ import print_function

import logging

from gsmmodem.modem import GsmModem, SentSms

# PORT = 'COM5' # ON WINDOWS, Port is from COM1 to COM9 ,
# We can check using the 'mode' command in cmd
PORT = '/dev/ttyUSB3'
BAUDRATE = 115200
SMS_TEXT = 'Hello'
SMS_DESTINATION = '004366066082107'
PIN = None  # SIM card PIN (if any)


def main():
    print('Initializing modem...')
    modem = GsmModem(PORT, BAUDRATE)
    print('Connect')
    modem.connect(PIN)
    print('Go')
    mytype=modem.model
    print('Model  '+modem.model)
    print('Imsi   '+modem.imsi)
    print('Signal '+str(modem.signalStrength))
    print('Network '+modem.networkName)
    print('SMSC    '+modem.smsc)
    modem.waitForNetworkCoverage(10)
    print('Sending SMS to: {0}'.format(SMS_DESTINATION))

    response = modem.sendSms(SMS_DESTINATION, SMS_TEXT)
    if type(response) == SentSms:
        print('SMS Delivered.')
    else:
        print('SMS Could not be sent')

    modem.close()


if __name__ == '__main__':
    main()
