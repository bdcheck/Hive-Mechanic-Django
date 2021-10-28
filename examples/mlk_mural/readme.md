This system requires Hive Mechanic to be running with and activity that has http integration and an api client setup.


###Required Software

- Python > 3.8
- pip

You can confirm your Python version by typing:
python3 --version
...if you see something 3.8 or less, you should update Python. For example, one tutorial on this: https://raspberrytips.com/install-latest-python-raspberry-pi/

You can see if pip is installed by typing:
python -m pip --version

###Installation Instructions

Create a virtual environment in the current directory
```
python3 -m venv venv
source ./venv/bin/activate
```
```
pip3 -r requirements.txt
```
Let the system install all the required software.

###Config
config.ini contains some information needed to connect and run the system
For some advanced configuration options look at the top of ml_mural.py

###Executing
make sure you have run
```
source ./venv/bin/activate
```
the nun using
```
python3 ml_mural.py
```
