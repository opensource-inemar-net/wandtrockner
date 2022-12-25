cd /usr/local/wandtrockner/oliver
python testcron.py | s6-log n20 s100000 T /usr/local/wandtrockner/logs/cronmin 2>&1

