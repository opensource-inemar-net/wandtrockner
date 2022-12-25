from flask import Flask, render_template, request, send_file, Response
import os
import datetime
from zipfile import ZipFile
from pathvalidate import sanitize_filepath
import shutil
import sys
import signal
if os.name != "nt":
    from gsmmodem.modem import GsmModem, SentSms

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'zip'} #for uploading new files
MAGIC_KEY = "inemar1808" #used to check if new version should be activated
LEARNING_DURATION = 240 #in minutes

PORT = '/dev/ttyUSB3'
BAUDRATE = 115200
#SMS_DESTINATION = '00436608937423'
PIN = None  # SIM card PIN (if any)
SEND_SMS = False
if os.name != "nt":
    SEND_SMS = True #Can be used to print sms text instead of sending one


@app.route('/', methods=['GET', 'POST'])
def index():
    
    app.logger.info("--------------- Hauptseite wurde aufgerufen :) ---------")
    
    file = open("../../../messung/modus.txt","r")
    modus = file.readline()
    file.close()
    
    file = open("../../../config/standort.txt","r")
    standort = file.readline()
    file.close()
    
    file = open("../../../config/smsziel.txt","r")
    smsziel = file.readline()
    file.close()
    
    file = open("../../../config/smserlaubt.txt","r")
    erlaubte_nummern = file.readline()
    file.close
    
    file = open("../../../config/device.txt","r")
    device = file.readline()
    file.close()
    
    file = open("../../../messung/verbrauch.txt","r")
    verbrauch = file.readline()
    file.close()
    
    file = open("../../../config/lernen.txt","r")
    lernzeit = file.readline()
    file.close()
    
    file = open("../../../messung/mittelwert.txt","r")
    mittelwert = file.readline()
    file.close()
    
    file = open("../../../messung/schwellwert.txt","r")
    schwellwert = file.readline()
    file.close()
    
    file = open("../magic.txt","r")
    version = file.readline()
    file.close()
    
    if request.method == 'POST':
        if request.form.get("new_standort") != None:
            if request.form.get("new_standort") != "":
                file = open("../../../config/standort.txt","w")
                file.write(request.form.get('new_standort'))
                standort = request.form.get('new_standort')
                file.close()
                # ----- Lernen starten -----
                file = open("../../../messung/modus.txt","w")
                file.write("Lernen")
                file.close()
                
                file = open("../../../config/lernen.txt","w")
                file.write((datetime.datetime.now()+datetime.timedelta(minutes=LEARNING_DURATION)).isoformat()) #learning time for LEARNING_DURATION minutes from now
                file.close()
                
        if request.form.get("end_lernen") == "Lernen beenden":
            file = open("../../../messung/modus.txt","w")
            file.write("Aktiv")
            file.close()
            
            file = open("../../../config/lernen.txt","w")
            file.write(datetime.datetime.now().isoformat())
            file.close()
            
        if request.form.get("setwlan") == "wlanstarten":
            print("Der WLAN Hotspot wird gestartet")
        if request.form.get("setwlan") == "wlanbeenden":
            print("Der WLAN Hotspot wird beendet")
            
        if request.form.get("Send SMS") == "Test SMS verschicken":
            #----- TODO: Datei für Tagesbericht anlegen -----
            pass
            
       #     text = "Das ist eine Test SMS"
       #     if SEND_SMS:
       # 
       #         app.logger.info("Try to send sms")
       #         app.logger.info('Initializing modem...')
       #         modem = GsmModem(PORT, BAUDRATE)
       #         modem.connect(PIN)
       #         
       #         file = open("../../../config/smsziel.txt", "r")
       #         smsziel = file.readline()
       #         file.close()
       #         smsziel = smsziel.split(smsziel,", ")
       #             
       #         for ziel in smsziel:
       #             dest = "00" + ziel[1:]
       #             
       #             app.logger.info("Waiting for network coverage...")
       #             modem.waitForNetworkCoverage(10)
       #             app.logger.info('Sending SMS to: {0}'.format(dest))
       #
       #             response = modem.sendSms(dest, text)
       #             if type(response) == SentSms:
       #                 app.logger.info('SMS Delivered.')
       #             else:
       #                 app.logger.info('SMS Could not be sent')
       #             modem.close()
       #     else:
       #         app.logger.info("SMS sending deactivated, would have sent SMS: " + text)
                
                
        if len(request.files) != 0 and request.files["new_version"].filename != "":
            new_version = request.files["new_version"]
            if new_version and '.' in new_version.filename and new_version.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                new_version.save("../../../version/" + new_version.filename)
                new_filename = "../../../version/" + new_version.filename.split(".")[0]
                with ZipFile("../../../version/" + new_version.filename, "r") as zip:
                    zip.extractall(new_filename)
                os.remove("../../../version/" + new_version.filename)
                valid = False
                try:
                    file = open(new_filename + "/" + "magic.txt","r")
                    for i, line in enumerate(file):
                        if i == 1:
                            if line == MAGIC_KEY:
                                valid = True
                    file.close()
                except:
                    app.logger.info("New Version file is not valid and won't be activated")
                    shutil.rmtree(new_filename, ignore_errors=True)
                if valid:
                    
                    
                    # Only in Linux!
                    if os.name != "nt":
                        app.logger.info("Console commands werden ausgeführt")
                        #res1=os.system("ln -sfn /usr/local/wandtrockner/oliver/test1   /usr/local/wandtrockner/oliver/active")
                        res1=os.system("ln -sfn /usr/local/wandtrockner/version/" + new_version.filename.split(".")[0] + "   /usr/local/wandtrockner/active/active")
                        app.logger.info("Result "+str(res1))
                        res2=os.system("sudo systemctl restart flask.service")
                        app.logger.info("Result2 "+str(res2))

                        #os.system("ln -sfn /usr/local/wandtrockner/version/V20221202-1500/   /usr/local/wandtrockner/active/active > /usr/local/wandtrockner/logs/cmd1.txt")
                        #os.system("sudo systemctl restart flask.service > /usr/local/wandtrockner/logs/cmd2.txt")
                    
                    app.logger.info("Server shutting down...")
                    
                    sig = getattr(signal, "SIGKILL", signal.SIGTERM)
                    os.kill(os.getpid(), sig)
                                        
                else:
                    shutil.rmtree(new_filename, ignore_errors=True)
                
                
            
            #More than 5 versions, delete the oldest
            while (len(os.listdir("../../../version")) > 5):
                versions = os.listdir("../../../version")
                versions.sort()
                shutils.rmtree("../../../version/" + versions[0])
        
        if request.form.get("new_zielnummer") != None:
            if smsziel != request.form.get("new_zielnummer") and len(request.form.get("new_zielnummer")) > 3:
                
                #Check if the input contains valid phonenumbers and reformat them
                zielnummern = request.form.get("new_zielnummer").split(", ")
                checked_zielnummern = ""

                for nummer in zielnummern:
                    nummer = nummer.strip()
                    for char in nummer[1:]:
                        if not char.isdecimal() and not char == " ":
                            break
                    else:
                        if nummer[:2] == "00":
                            nummer = "+" + nummer[2:]
                            checked_zielnummern += nummer.replace(" ", "") + ", "
                        elif nummer[0] == "0":
                            nummer = "+43" + nummer[1:]
                            checked_zielnummern += nummer.replace(" ", "") + ", "
                        elif nummer[0] == "+":
                            checked_zielnummern += nummer.replace(" ", "") + ", "
                        else:
                            continue
                
                #Save the new phonenumbers
                file = open("../../../config/smsziel.txt","w")
                file.write(checked_zielnummern)
                smsziel = checked_zielnummern
                file.close()
                
        if request.form.get("new_erlaubte_nummern") != None:
            if erlaubte_nummern != request.form.get("new_erlaubte_nummern") and len(request.form.get("new_erlaubte_nummern")) > 3:
                
                erlaubte_nummern = request.form.get("new_erlaubte_nummern").split(", ")
                checked_erlaubte_nummern = ""

                #Check if the input contains valid phonenumbers and reformat them
                for nummer in erlaubte_nummern:
                    nummer = nummer.strip()
                    for char in nummer[1:]:
                        if not char.isdecimal() and not char == " ":
                            break
                    else:
                        if nummer[:2] == "00":
                            nummer = "+" + nummer[2:]
                            checked_erlaubte_nummern += nummer.replace(" ", "") + ", "
                        elif nummer[0] == "0":
                            nummer = "+43" + nummer[1:]
                            checked_erlaubte_nummern += nummer.replace(" ", "") + ", "
                        elif nummer[0] == "+":
                            checked_erlaubte_nummern += nummer.replace(" ", "") + ", "
                        else:
                            continue
                
                #Save the new phonenumbers
                file = open("../../../config/smserlaubt.txt","w")
                file.write(checked_erlaubte_nummern)
                erlaubte_nummern = checked_erlaubte_nummern
                file.close()
        if request.form.get("protokoll_laden") == "Protokoll herunterladen":
            return download_data()
        if request.form.get("logs_laden") == "Logs herunterladen":
            return download_logs()
    
    
    if modus == "Aktiv":
        moduscolor = "green"
    elif modus == "Lernen":
        moduscolor = "blue"
    else:
        moduscolor = "red"
        
    
    return render_template("index.html", modus=modus, moduscolor=moduscolor, standort=standort, zielnummer=smsziel, erlaubte_nummern=erlaubte_nummern, device=device, uhrzeit=datetime.datetime.now().strftime("%H:%M"), verbrauch=verbrauch, version=version, lernzeit=datetime.datetime.fromisoformat(lernzeit).strftime("%H:%M"), mittelwert=mittelwert, schwellwert=schwellwert)

#@app.route('/downloadlogs')
def download_logs():
    logpath = "../../../logs"
    #with ZipFile(path+"logs.zip", "w") as newzip:
    #    newzip.write(path+"cronmin/active", arcname="activelogs.txt")
    #return send_file(path+"logs.zip", as_attachment=True)
    try:
        # Only in Linux!
        if os.name != "nt":
            app.logger.info("Console command getlog.sh wird ausgeführt")
            os.system("/usr/local/wandtrockner/active/active/scripts/getlog.sh")
        
        shutil.make_archive("../../../messung/logs","zip",logpath)
    except:
        app.logger.info("Error while creating zip of requested logdata")
        
    app.logger.info("Sending logdata for download")
    return send_file("../../../messung/logs.zip", as_attachment=True)


#@app.route('/downloaddata')
def download_data():
    file = open("../../../config/standort.txt","r")
    standort = file.readline()
    file.close()
    path = "../../../daten/"+sanitize_filepath(standort) +"-daten.csv"
    
    #path = "../../../daten/"+sanitize_filepath(standort) +"-daten."
    #try:
    #    with ZipFile(path+"zip", "w") as newzip:
    #        newzip.write(path+"csv", arcname=sanitize_filepath(standort) +"-daten.csv")
    #except:
    #    return Response(status=204)
    if os.path.isfile(path):
        app.logger.info("Sending measurement data for download")
        return send_file(path, as_attachment=True)
    else:
        app.logger.info("Request for data invalid, requested file not found")
        return Response(status=204)
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
