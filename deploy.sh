#!/bin/bash
if [ $# -eq 1 ]
  then
    echo Deploying scripts to host $1
    rsync --progress -avz --exclude '.git' --exclude '.DS_Store' --exclude 'system' --exclude 'conf' --exclude 'deploy.sh' --exclude 'libs' --exclude '.idea' --exclude '*.pyc' --exclude 'libs/cherrypy/build' --exclude 'CherryPy.egg*' --exclude '.CherryPy*' \
        --exclude 'cherrypy/dist' --exclude 'libs/pigpio' \
        -e "ssh -A -t pi@$1" . :/home/pi/schnee-eulen
fi


# rsync files to master 10.0.0.1
#rsync --progress -avz --exclude '.git' --exclude 'system' --exclude '.idea' --exclude '*.pyc' --exclude 'libs/cherrypy/build' --exclude 'CherryPy.egg*' --exclude '.CherryPy*' --exclude 'cherrypy/dist' --exclude 'libs' \
#    -e "ssh -A -t pi@10.0.0.1" . :/home/pi/schnee-eulen/

# rsync files to slave owl-slave-01
#rsync --progress -avz --exclude '.git' --exclude 'system' --exclude '.idea' --exclude '*.pyc' --exclude 'libs/cherrypy/build' --exclude 'CherryPy.egg*' --exclude '.CherryPy*' --exclude 'cherrypy/dist' --exclude 'libs' \
#    -e "ssh owl-slave-01" . :/home/pi/schnee-eulen/

# rsync files to slave owl-slave-02
#rsync --progress -alvz --exclude '.git' --exclude 'system' --exclude '.idea' --exclude '*.pyc' --exclude 'libs/cherrypy/build' --exclude 'CherryPy.egg*' --exclude '.CherryPy*' --exclude 'cherrypy/dist' --exclude 'libs' \
#    -e "ssh owl-slave-02" . :/home/pi/schnee-eulen/

# to make commands to slave work with external (non-wlan) ip, best use this in .ssh/config:
#
#Host owl-master
#        HostName 192.168.3.5
#        User pi
#
#Host owl-slave-01
#        HostName 10.0.0.76
#        ForwardAgent yes
#        User pi
#        IdentityFile ~/.ssh/id_rsa
#        ProxyCommand ssh -q owl-master nc -q0 %h 22
