date > /usr/local/wandtrockner/logs/date.txt
journalctl --since="3d ago" >/usr/local/wandtrockner/logs/journal.txt
ip addr show  >/usr/local/wandtrockner/logs/ip.txt
top -n 1  >/usr/local/wandtrockner/logs/top.txt


