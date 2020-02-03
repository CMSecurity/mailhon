# Mailhon - Yet Another Mail Honeypot
mailhon is a minimalistic mail honeypot based on Pythons aiosmptd.  
The server emulates an open relay and saves every interaction in a json log.  
Currently, only emulation for exim4 is supported, but the architecture is expandable with little effort as it is built in a modular way.  
The logs can i.e. be collected by an ELK or Splunk instance.

## Setup
The only requirement needed for mailhon to work are aiosmtpd and Python 3.6+.
Although these are light requirements, running mailhon in a virtualenv is still highly recommended.  
A new Python 3 environment can be created with `python3 -m venv venv`.
To install the requirements into the newly created venv, run `venv/bin/pip install -r requirements.txt`.
Afterwards, the venv can either be activated (`source venv/bin/activate`) or used directly to run the server (`venv/bin/python mailpot/server.py`).

## Running Mailhon
With your environment prepared, run `python mailpot/server.py`. All interaction will be logged in `mails.json`.

## Open TODOs
- [ ] Introduce config  
- [ ] Send n number of mails out before nulling them (trick live checks)  
- [ ] Add more mailservers  