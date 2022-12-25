cd /usr/local/wandtrockner/active/active/python
python cronjob.py  | s6-log n20 s100000 T /usr/local/wandtrockner/logs/cronmin 2>&1
