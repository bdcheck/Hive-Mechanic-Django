This system requires Hive Mechanic to be running with and activity that has http integration and an api client setup.


###Required Software

- Python > 3.7.3
- pip
- LibSDL 2.0 with libSDL-Image 2.0 and LibSDL-mixer 2.0 

### Installation Instructions

Create a virtual environment in the current directory
```
python3 -m venv venv
source ./venv/bin/activate
```
```
pip3 install -r requiresents.txt
```
Let the system install all the required software.

### Config
config.ini contains some information needed to connect and run the system
For some advanced configuration options look at the top of ml_mural.py

### Executing
make sure you have run
```
source ./venv/bin/activate
```
the nun using
```
python3 ml_mural.py
```
