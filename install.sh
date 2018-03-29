#!/usr/bin/env bash

SERVICE="sibus.web.server"

INSTALL_DIR=`pwd`
SERVICE_PATH="$INSTALL_DIR/sibus.server.py"
SYSTEMD_SERVICE="$SERVICE.service"
SYSTEMD_ORG="$INSTALL_DIR/systemd-config"
SYSTEMD_TMP="$INSTALL_DIR/$SYSTEMD_SERVICE"
SYSTEMD_DST="/lib/systemd/system/$SYSTEMD_SERVICE"

echo " # Update folder from git repository"
git fetch origin master
git reset --hard origin/master

if [ ! -e $SERVICE_PATH ]; then
    echo " !!! ERROR: file $SERVICE_PATH not found !!!"
    echo " (script must be run from its own directory !)"
    exit 1
fi
sudo chmod +x $SERVICE_PATH

echo " # Checking service $SERVICE dependencies"

sudo pip install --upgrade flask sibus_lib

echo " # Patching service $SERVICE systemd config file..."
sed 's|<SCRIPT_PATH>|'$SERVICE_PATH'|g' $SYSTEMD_ORG > "/tmp/tmp.systemd"
sed 's|<SCRIPT_DIR>|'$INSTALL_DIR'|g' "/tmp/tmp.systemd" > "/tmp/tmp2.systemd"
sed 's|<USER>|'$USER'|g' "/tmp/tmp2.systemd" > $SYSTEMD_TMP
echo " = systemd config: "
cat $SYSTEMD_TMP

echo " # Installing service $SERVICE"
sudo cp -fv $SYSTEMD_TMP $SYSTEMD_DST
sudo systemctl daemon-reload

echo " # Enable & start service $SERVICE at boot"
sudo systemctl enable $SYSTEMD_SERVICE
sudo systemctl start $SYSTEMD_SERVICE

echo " # Service $SERVICE status"
sudo systemctl status $SYSTEMD_SERVICE
exit 0

