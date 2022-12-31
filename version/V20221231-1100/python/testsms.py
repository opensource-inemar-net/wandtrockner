"""Test sending SMS"""

from gsmmodem.modem import GsmModem, SentSms


PORT = '/dev/ttyUSB3'
BAUDRATE = 115200
SMS_TEXT = 'Hello Martin!'
SMS_DESTINATION = '00436608937423'
PIN = None  # SIM card PIN (if any)



def main():
    print('Initializing modem...')
    modem = GsmModem(PORT, BAUDRATE)
    print('Connect')
    modem.connect(PIN)
    print('Go')
    mytype=modem.model
    #print('Model  '+modem.model)
    #print('Imsi   '+modem.imsi)
    #print('Signal '+str(modem.signalStrength))
    #print('Network '+modem.networkName)
    #print('SMSC    '+modem.smsc)
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
