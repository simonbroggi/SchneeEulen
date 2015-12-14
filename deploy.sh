# rsync files to master 10.0.0.1
rsync --progress -avz --exclude '.git' --exclude 'system' --exclude '.idea' --exclude '*.pyc' --exclude 'libs/cherrypy/build' --exclude 'CherryPy.egg*' --exclude '.CherryPy*' --exclude 'cherrypy/dist' --exclude 'libs' \
    -e "ssh -A -t pi@192.168.3.5" . :/home/pi/schnee-eulen/

# rsync files to slave owl-slave-01
rsync --progress -avz --exclude '.git' --exclude 'system' --exclude '.idea' --exclude '*.pyc' --exclude 'libs/cherrypy/build' --exclude 'CherryPy.egg*' --exclude '.CherryPy*' --exclude 'cherrypy/dist' --exclude 'libs' \
    -e "ssh owl-slave-01" . :/home/pi/schnee-eulen/

# to make commands to slave work, best use this in .ssh/config:
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
