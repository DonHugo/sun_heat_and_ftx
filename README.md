# sun_heat_and_ftx

## install software for sequentmicrosystems boards

### RTD Data Acquisition:
```
https://sequentmicrosystems.com/pages/rtd-data-acquisition-downloads
```
```
~$ sudo apt-get update
~$ sudo apt-get install build-essential python-pip python-dev python-smbus git
~$ git clone https://github.com/SequentMicrosystems/rtd-rpi.git
~$ cd rtd-rpi/python/rtd/
~/rtd-rpi/python/rtd$ sudo python3 setup.py install
```
### Building Automation V4 
```
https://sequentmicrosystems.com/pages/building-automation-downloads
```
```
~$ sudo apt-get update
~$ sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
~$ git clone https://github.com/SequentMicrosystems/megabas-rpi.git
~$ cd megabas-rpi/python/
~/megabas-rpi/python$ sudo python3 setup.py install
```
### Four Relays four HV Inputs 
```
https://sequentmicrosystems.com/pages/four-relays-four-inputs-downloads
```
```
~$ sudo apt-get update
~$ sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
~$ git clone https://github.com/SequentMicrosystems/4relind-rpi.git
~$ cd 4relind-rpi/python/4relind/
~/4relind-rpi/python/4relind$ sudo python3 setup.py install
```
## pypi:
```
pip3 install statistics
pip3 install numpy
pip3 install paho-mqtt

```
## Application

### installation
copy this file to /etc/systemd/system/
```
sudo cp temperature_monitoring.service /etc/systemd/system/
```
### usage
start the service
```
sudo systemctl start temperature_monitoring.service
```
stop the service
```
sudo systemctl stop temperature_monitoring.service        
```
restart the servic
```
sudo systemctl restart temperature_monitoring.service       
```
Get the current status of the service
```
sudo systemctl status temperature_monitoring.service      
```
enable the service to start automatically at boot
```
sudo systemctl enable temperature_monitoring.service
```
disable automatic start at boot
```
sudo systemctl disable temperature_monitoring.service     
```
Make sure to reload systemd after making any changes to the service file
```
sudo systemctl daemon-reload                              
```