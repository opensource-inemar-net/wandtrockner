cd /usr/local/wandtrockner/active/active/flask
python webapp.py | s6-log n20 s100000 T /usr/local/wandtrockner/logs/flask 2>&1
