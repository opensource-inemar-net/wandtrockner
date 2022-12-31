"""Resets the system to start value, used for debugging"""





file = open("../../../messung/alarm_werthoch.txt", "w")
file.write("0")
file.close()

file = open("../../../messung/alarm_wertniedrig.txt", "w")
file.write("0")
file.close()

file = open("../../../messung/alarm_keinstrom.txt", "w")
file.write("0")
file.close()

file = open("../../../messung/mittelwert.txt", "w")
file.write("0")
file.close()

file = open("../../../messung/schwellwert.txt", "w")
file.write("0")
file.close()

file = open("../../../messung/verbrauch.txt", "w")
file.write("0")
file.close()

