#import pymodbus
from pyModbusTCP.client import ModbusClient
import sys
import csv
from pathvalidate import sanitize_filepath
from gsmmodem.modem import GsmModem, SentSms
import datetime
import os
import logging


PORT = '/dev/ttyUSB3'
#BAUDRATE = 115200
BAUDRATE = 19200
#SMS_DESTINATION = '00436608937423'
PIN = None  # SIM card PIN (if any)

LEARNING_DURATION = 240 #in minutes
SEND_SMS = True #Can be used to print sms text instead of sending one
HELPTEXT = "Diese Befehle sind möglich:\nhilfe - Erhalte SMS mit möglichen Kommandos\nstandort [xxx] - Speichert die Zeichen nach 'standort ' als neuen Standort\nlernen - Startet lernen\nfertig - Stoppt lernen\nstatus - Versendet eine Statusmeldung\npause - Verhindert das Senden von Warnung für 24 Stunden\nhotspot an - Aktiviert Hotspot\nhotspot aus - Bucht in WLAN ein"
    

def check_sms(modem):
    print("Checking for sms...")
    if modem == None:
        print("Modem not connected")
        return
    #try:
    #    modem = GsmModem(PORT, BAUDRATE)
    #    print("Modem set")
    #    modem.connect(PIN)
    #    print("Connection successful")
    #except:
    #    print("Error while checking for SMS, connection failed")
    #    return
    
    messages = modem.listStoredSms(delete=True)
        
    print("There are {} new messages".format(len(messages)))
    for message in messages:
        print("New message")
        print(message.number)
        print(message.text)
        file = open("../../../messung/smseingang.txt","w")
        file.write(message.text + ", " + str(message.number))
        file.close()
        
        # ----- Check the content of the sms -----
        text = message.text.strip().lower()
        
        if text == "help" or text == "hilfe":
            file = open("../../../messung/sms/help.txt","w")
            file.write("This file indicates that the system is trying to send a sms with possible sms commands")
            file.close()
        if text[:8] == "standort":
            file = open("../../../config/standort.txt","w")
            file.write(text[9:])
            file.close()
        if text == "lernen":
            activate_learning()
        if text == "fertig":
            file = open("../../../config/lernen.txt","w")
            file.write(datetime.datetime.now().isoformat())
            file.close()
            set_mode("Aktiv")
        if text == "status":
            file = open("../../../messung/sms/dailyreport.txt","w")
            file.write("This file indicates that the system is trying to send a report sms")
            file.close()
        if text == "pause":
            file = open("../../../messung/sms/pause.txt","w")
            file.write((datetime.datetime.now()+datetime.timedelta(hours=24)).isoformat())
            file.close()
        if text == "hotspot an":
            print("Der WLAN Hotspot wird gestartet")
            os.system("bash /usr/local/wandtrockner/active/active/script/actspot.sh")
        if text == "hotspot aus":
            app.logger.info("Der WLAN Hotspot wird beendet")
            os.system("bash /usr/local/wandtrockner/active/active/script/dactspot.sh")
            

    #modem.close()
    return


# values is a list of integers with len>0
def int_from_registervalue(values, factor=1):
    """Takes a list of decimal integer values between 0 and 65536 that 
        represent hex numbers from 16 Byte Registers, converts them to a single integer
        and multiplies a factor (to change the unit measurement i.e. from mV to V)"""
    result = ""  #hex(values[0]))
    for value in values:
        result += ("000"+hex(value)[2:])[-4:]
    return int(result,16)*factor
    
def activate_learning():
    """Activates learning mode by writing to modus.txt and set new ending time in lernen.txt"""
    file = open("../../../config/lernen.txt","w")
    file.write((datetime.datetime.now()+datetime.timedelta(minutes=LEARNING_DURATION)).isoformat()) #learning time for LEARNING_DURATION minutes from now
    file.close()
    
    file = open("../../../messung/alarm_wertniedrig.txt", "w")
    file.write("0")
    file.close()
    
    file = open("../../../messung/alarm_werthoch.txt", "w")
    file.write("0")
    file.close()
    
    file = open("../../../messung/alarm_keinstrom.txt", "w")
    file.write("0")
    file.close()
    
    
    set_mode("Lernen")
    return
    
def reset_alarm():
    """Checks all alarm counters, sets them to 0 and sends a sms if an alarm was triggered"""
    
    file = open("../../../messung/alarm_werthoch.txt", "r")
    alarm_werthoch = file.readline()
    file.close()
    
    if int(alarm_werthoch) >= 5:
        file = open("../../../messung/alarm_werthoch.txt", "w")
        file.write("0")
        file.close()
        send_sms("Der Stromverbrauch war zu hoch, ist jetzt aber wieder normal.")
    elif alarm_werthoch != "0":
        file = open("../../../messung/alarm_werthoch.txt", "w")
        file.write("0")
        file.close()
        
    file = open("../../../messung/alarm_wertniedrig.txt", "r")
    alarm_wertniedrig = file.readline()
    file.close()
    
    if int(alarm_wertniedrig) >= 5:
        file = open("../../../messung/alarm_wertniedrig.txt", "w")
        file.write("0")
        file.close()
        send_sms("Der Stromverbrauch war zu niedrig, ist jetzt aber wieder normal.")
    elif alarm_wertniedrig != "0":
        file = open("../../../messung/alarm_wertniedrig.txt", "w")
        file.write("0")
        file.close()


    file = open("../../../messung/alarm_keinstrom.txt", "r")
    alarm_keinstrom = file.readline()
    file.close()
    
    if int(alarm_keinstrom) >= 5:
        file = open("../../../messung/alarm_keinstrom.txt", "w")
        file.write("0")
        file.close()
        send_sms("Die Stromversorgung war unterbrochen, ist jetzt aber wieder normal.")
    elif alarm_keinstrom != "0":
        file = open("../../../messung/alarm_keinstrom.txt", "w")
        file.write("0")
        file.close()
    
    return
    
def set_mode(modus):
    """Takes a string indicating a mode of the system and writes it to mudus.txt"""
    file = open("../../../messung/modus.txt","w")
    file.write(modus)
    file.close()
    return
    
def send_sms(text,modem):
    """Sends a sms containing the received text"""
    if modem == None:
        print("No connection to the modem")
        return False
    
    if SEND_SMS:
        
        print("Try to send sms")
        #print('Initializing modem...')
        #try:
        #    modem = GsmModem(PORT, BAUDRATE)
        #    print("Modem set")
        #    modem.connect(PIN)
        #    print("Connection successful")
        #except:
        #    print("Error while trying to send SMS, connection failed")
        #    return False
        
        if not os.path.isfile("../../../config/smsziel.txt"):
            print("No file smsziel.txt found")
            file = open("../../../config/smsziel.txt", "w")
            file.close()
            return False
        file = open("../../../config/smsziel.txt", "r")
        smsziel = file.readline()
        file.close()
        smsziel = smsziel.split(", ")
        
        print("SMS destination found, trying to send")
        for ziel in smsziel:
            if len(ziel) > 5:
                #dest = "00" + ziel[1:]
                dest = ziel
                print("Waiting for network coverage...")
                try:
                    resp = modem.waitForNetworkCoverage(20)
                    print(resp)
                except:
                    print("No network coverage")
                    return False
                print('Sending SMS to: {0}'.format(dest))
                print("Text: " + text)

                try:
                    modem.smsTextMode = False
                    response = modem.sendSms(dest, text, deliveryTimeout=30)
                    print(response)
                    if type(response) == SentSms:
                        print('SMS Delivered.')
                    else:
                        print('SMS Could not be sent')
                        return False
                except Exception as e:
                    print("Exception occured")
                    print(e)
                    return False
                print("SMS should be on its way")
                

        #modem.close()
    else:
        print("SMS sending deactivated, would have sent SMS: " + text)
    return True


def cronjob():

    print("---------------------------------------------------------")
    print("Starting the cronjob")
    
    
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)
    
    print("Try to connect to modem")
    modem = None
    try:
        modem = GsmModem(PORT, BAUDRATE, requestDelivery=False)
        print("Modem set")
        modem.connect(PIN,waitingForModemToStartInSeconds=15)
        print("Connection successful")
        #modem.smsTextMode = True
    except Exception as e:
        print("Error while connecting to modem, connection failed")
        print(e)
        modem = None
    
    
    #if modem != None:
    #    modem.timeActivateNITZ()
    
    

    # ----- Establish connection to the Energy Meter ---------
    client = ModbusClient(host="192.168.1.249", port = 502, auto_open=True,debug=True)
    print("Opening connection")
    client.open()
    
    print("Reading data...")
    data = client.read_holding_registers(0,65) #get all the data needed
    
    if data == None:
        print("No connection to Energy Meter")
        alarmfile = open("../../../messung/alarm_keinstrom.txt", "r")
        alarm_counter = alarmfile.readline()
        alarmfile.close()
        set_mode("Kein Strom")
        if int(alarm_counter) == 4:
            file = open("../../../messung/sms/nopower.txt","w")
            file.write("There is no Ethernet connection for 5 minutes, the system is now trying to send a sms")
            file.close()
        alarmfile = open("../../../messung/alarm_keinstrom.txt", "w")
        alarmfile.write(str(int(alarm_counter)+1))
        alarmfile.close()
        return
    
    # ----- Read and print data -------
    print("Data:")

    voltage_phase1 = int_from_registervalue([data[0],data[1]],0.001)
    voltage_phase2 = int_from_registervalue([data[2],data[3]],0.001)
    voltage_phase3 = int_from_registervalue([data[4],data[5]],0.001)
    voltage_system = int_from_registervalue([data[12],data[13]],0.001)

    #print("Voltage Phase 1: " + str(voltage_phase1) + " V")
    #print("Voltage Phase 2: " + str(voltage_phase2) + " V")
    #print("Voltage Phase 3: " + str(voltage_phase3) + " V")
    #print("System Voltage: " + str(voltage_system) + " V")
    #print()

    current_phase1 = int_from_registervalue([data[14],data[15]],0.001)
    current_phase2 = int_from_registervalue([data[16],data[17]],0.001)
    current_phase3 = int_from_registervalue([data[18],data[19]],0.001)
    current_neutral = int_from_registervalue([data[20],data[21]],0.001)
    current_system = int_from_registervalue([data[22],data[23]],0.001)

    #print("Current Phase 1: " + str(current_phase1) + " A")
    #print("Current Phase 2: " + str(current_phase2) + " A")
    #print("Current Phase 3: " + str(current_phase3) + " A")
    #print("Neutral Current: " + str(current_neutral) + " A")
    #print("System Current: " + str(current_system) + " A")
    #print()

    activepower_phase1 = int_from_registervalue([data[28],data[29],data[30]],0.001)
    activepower_phase2 = int_from_registervalue([data[31],data[32],data[33]],0.001)
    activepower_phase3 = int_from_registervalue([data[34],data[35],data[36]],0.001)
    activepower_system = int_from_registervalue([data[37],data[38],data[39]],0.001)

    print("Phase 1 active power: " + str(activepower_phase1) + " W")
    print("Phase 2 active power: " + str(activepower_phase2) + " W")
    print("Phase 3 active power: " + str(activepower_phase3) + " W")
    print("System active power: " + str(activepower_system) + " W")


    #print("Phase 1 apparent power: " + str(int(hex(data[40]) + ("000"+hex(data[41])[2:])[-4:] + ("000"+hex(data[42])[2:])[-4:],16)/1000) + " VA")
    #print("Phase 2 apparent power: " + str(int(hex(data[43]) + ("000"+hex(data[44])[2:])[-4:] + ("000"+hex(data[45])[2:])[-4:],16)/1000) + " VA")
    #print("Phase 3 apparent power: " + str(int(hex(data[46]) + ("000"+hex(data[47])[2:])[-4:] + ("000"+hex(data[48])[2:])[-4:],16)/1000) + " VA")
    #print("System apparent power: " + str(int(hex(data[49]) + ("000"+hex(data[50])[2:])[-4:] + ("000"+hex(data[51])[2:])[-4:],16)/1000) + " VA")
    #print()
    #print("Phase 1 reactive power: " + str(int(hex(data[52]) + ("000"+hex(data[53])[2:])[-4:] + ("000"+hex(data[54])[2:])[-4:],16)/1000) + " var")
    #print("Phase 2 reactive power: " + str(int(hex(data[55]) + ("000"+hex(data[56])[2:])[-4:] + ("000"+hex(data[57])[2:])[-4:],16)/1000) + " var")
    #print("Phase 3 reactive power: " + str(int(hex(data[58]) + ("000"+hex(data[59])[2:])[-4:] + ("000"+hex(data[60])[2:])[-4:],16)/1000) + " var")
    #print("System reactive power: " + str(int(hex(data[61]) + ("000"+hex(data[62])[2:])[-4:] + ("000"+hex(data[63])[2:])[-4:],16)/1000) + " var")
    #print()
    print("Frequency: " + str(data[64]/1000))


    
    #Get standort of the device
    file = open("../../../config/standort.txt", "r")
    standort = file.readline()
    file.close()
    
    #--------- Write data to csv file --------
    #gsmtime = modem.time
    #print("Time of the gsm modem: ")
    #print(gsmtime)
    
    if not os.path.isfile("../../../daten/" + sanitize_filepath(standort) +"-daten.csv"):
        #new .csv file
        datafile = open("../../../daten/" + sanitize_filepath(standort) +"-daten.csv", "w", encoding='UTF8', newline='')
        datafile_writer = csv.writer(datafile)
        datafile_writer.writerow(["Zeit des Geräts", "Standort", "Voltage Phase 1 (V)", "Voltage Phase 2 (V)", "Voltage Phase 3 (V)", "System Voltage (V)", "Current Phase 1 (A)", "Current Phase 2 (A)", "Current Phase 3 (A)", "Neutral Current (A)", "System Current (A)", "Active Power Phase 1 (W)", "Active Power Phase 2 (W)", "Active Power Phase 3 (W)", "System Active Power (W)"])
        datafile_writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),standort,voltage_phase1,voltage_phase2,voltage_phase3,voltage_system,current_phase1,current_phase2,current_phase3,current_neutral,current_system,activepower_phase1,activepower_phase2,activepower_phase3,activepower_system])
        datafile.close()
    else:
        #add to existing file
        datafile = open("../../../daten/" + sanitize_filepath(standort) +"-daten.csv", "a", encoding='UTF8', newline='')
        datafile_writer = csv.writer(datafile)
        datafile_writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d"),standort,voltage_phase1,voltage_phase2,voltage_phase3,voltage_system,current_phase1,current_phase2,current_phase3,current_neutral,current_system,activepower_phase1,activepower_phase2,activepower_phase3,activepower_system])
        datafile.close()
        
    # ----- Write new active power value to file -----
    verbrauchfile = open("../../../messung/verbrauch.txt", "w")
    verbrauchfile.write(str(activepower_system))
    verbrauchfile.close()
    
    # ----- Calculate and write average power over the last measurements to file -------
    mittelwertfile = open("../../../messung/mittelwert.txt", "r")
    mittelwert = mittelwertfile.readline()
    mittelwertfile.close()
    
    mittelwertfile = open("../../../messung/mittelwert.txt", "w")
    if mittelwert == "":
        # ~ mittelwert = str(activepower_system)
        mittelwertfile.write(mittelwert)
    else:
        mittelwert = str(float(mittelwert)*0.8 + activepower_system*0.2)
        mittelwertfile.write(mittelwert)
    mittelwertfile.close()
    mittelwert = float(mittelwert)
    
    # ----- Check if learning is active -----
    lernfile = open("../../../config/lernen.txt", "r")
    lernzeit = lernfile.readline()
    lernfile.close()
    modefile = open("../../../messung/modus.txt","r")
    mode = modefile.readline()
    modefile.close()
    
    lernen_aktiv = False
    if lernzeit > datetime.datetime.now().isoformat():
        # Learning is active
        lernen_aktiv = True
    else:
        if mode == "Lernen":
            #End learning mode
            #modefile = open("../../../messung/modus.txt","w")
            #modefile.write("Aktiv")
            #modefile.close()
            set_mode("Aktiv")
            
    
    file = open("../../../messung/modem.txt", "w")
    if modem != None:
        file.write(modem.imsi + "," + modem.signalStrengh + "," + modem.write('AT+CPSI?'))
    else:
        file.write("Keine Verbindung" + "," + "Keine Verbindung" + "," + "Keine Verbindung")
    file.close()
    # ----- Compare average power with the threshold value for the alarm -----
    schwellwertfile = open("../../../messung/schwellwert.txt", "r")
    schwellwert = schwellwertfile.readline()
    schwellwertfile.close()
    
    if mittelwert > (float(schwellwert)*1.1) and mittelwert-float(schwellwert) > 3: #Power consumption too high
        if lernen_aktiv:
            print("Reset learning - higher power")
            print("From: " + schwellwert + " To: " + str(mittelwert))
            schwellwertfile = open("../../../messung/schwellwert.txt", "w")
            schwellwertfile.write(str(mittelwert))
            schwellwertfile.close()
            activate_learning()
        else:
            alarmfile = open("../../../messung/alarm_werthoch.txt", "r")
            alarm_counter = alarmfile.readline()
            alarmfile.close()
            alarmfile = open("../../../messung/alarm_werthoch.txt", "w")
            alarmfile.write(str(int(alarm_counter)+1))
            alarmfile.close()
            set_mode("Stromverbrauch gestiegen")
            if int(alarm_counter) == 5:
                print("Alarm counter powwer_high equals 5, sending SMS")
                file = open("../../../messung/sms/powerhigh.txt","w")
                file.write("The power consumption is too high for 5 minutes, the system is now trying to send a sms")
                file.close()
                #send_sms("Der Stromverbrauch am Standort {} ist plötzlich gestiegen".format(standort))
    elif mittelwert < (float(schwellwert)*0.9) and float(schwellwert)-mittelwert > 3: #Power consumption too low
        if lernen_aktiv:
            print("Reset learning - lower power")
            print("From: " + schwellwert + " To: " + str(mittelwert))
            schwellwertfile = open("../../../messung/schwellwert.txt", "w")
            schwellwertfile.write(str(mittelwert))
            schwellwertfile.close()
            activate_learning()
        else:
            print("Alarm, power consumption too low")
            alarmfile = open("../../../messung/alarm_wertniedrig.txt", "r")
            alarm_counter = alarmfile.readline()
            alarmfile.close()
            alarmfile = open("../../../messung/alarm_wertniedrig.txt", "w")
            alarmfile.write(str(int(alarm_counter)+1))
            alarmfile.close()
            set_mode("Stromverbrauch gesunken")
            if int(alarm_counter) == 5:
                print("Alarm counter power_low equals 5, sending SMS")
                file = open("../../../messung/sms/powerlow.txt","w")
                file.write("The power consumption is too low for 5 minutes, the system is now trying to send a sms")
                file.close()
                #send_sms("Der Stromverbrauch am Standort {} ist plötzlich gesunken".format(standort))
    else:
        print("Alarm is over, reseting alarm counter and mode")
        reset_alarm()
        set_mode("Aktiv")
    
    if os.path.isfile("../../../messung/sms/bootreport.txt"):
        if send_sms("Das System am Standort {} wurde aktiviert und misst den Stromverbrauch.".format(standort),modem):
            os.remove("../../../messung/sms/bootreport.txt")
    if os.path.isfile("../../../messung/sms/dailyreport.txt"):
        #if send_sms("Hallo",modem):
        if send_sms("Statusmeldung: Es ist {} Uhr, das System am Standort {} ist im Modus {} und der aktuelle Stromverbrauch beträgt {}".format(datetime.datetime.now().strftime("%H:%M"),standort,mode,activepower_system),modem):
            os.remove("../../../messung/sms/dailyreport.txt")
    if os.path.isfile("../../../messung/sms/help.txt"):
        if send_sms(HELPTEXT,modem):
            os.remove("../../../messung/sms/help.txt")
    if not os.path.isfile("../../../messung/sms/pause.txt"):
        if os.path.isfile("../../../messung/sms/powerlow.txt"):
            if send_sms("Der Stromverbrauch am Standort {} ist plötzlich gesunken".format(standort),modem):
                os.remove("../../../messung/sms/powerlow.txt")
        if os.path.isfile("../../../messung/sms/powerhigh.txt"):
            if send_sms("Der Stromverbrauch am Standort {} ist plötzlich gestiegen".format(standort),modem):
                os.remove("../../../messung/sms/powerhigh.txt")
        if os.path.isfile("../../../messung/sms/nopower.txt"):
            if send_sms("Der Strom am Standort {} ist ausgefallen".format(standort),modem):
                os.remove("../../../messung/sms/nopower.txt")
            
    
    if os.path.isfile("../../../messung/sms/pause.txt"):
        file = open("../../../messung/sms/pause.txt","w")
        deletetime = file.readline()
        file.close()
        if deletetime < datetime.datetime.now().isoformat():
            os.remove("../../../messung/sms/pause.txt")
    
    check_sms(modem)
    if modem != None:
        modem.close()
    print("Finished cronjob")
        
    

if __name__ == '__main__':
    cronjob()
