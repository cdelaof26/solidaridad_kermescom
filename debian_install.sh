#!/bin/bash

clone () {
# Pre setup
sudo apt install -y git
cd ~
git clone https://github.com/cdelaof26/solidaridad_kermescom.git
cd ~/solidaridad_kermescom
}

dependency_install () {
# Part 1 - Install dependencies
echo "Installing dependencies..."
sleep 3

sudo apt update
sudo apt install -y wget gnupg python3 python3-pip python3-venv

wget https://dev.mysql.com/get/mysql-apt-config_0.8.36-1_all.deb
sudo python3 -m pip install pexpect --quiet --break-system-packages
if [ $? -ne 0 ]; then
	echo "Failed to install pexpect. Exiting with code 1"
	exit 1
fi;
}


mysql_install () {
# Part 2 - Install MySQL
# https://geert.vanderkelen.org/2018/mysql8-unattended-dpkg/
echo "Installing mysql..."
sleep 3

cat <<EOF > install_mysql_aptsrc.py
import pexpect
import time
child = pexpect.spawn('dpkg -i mysql-apt-config_0.8.36-1_all.deb')
child.expect('<Ok>')
child.sendline('\033[B')
time.sleep(1)
child.sendline('\033[B')
time.sleep(1)
child.sendline('\r')
child.wait()
EOF

sudo python3 install_mysql_aptsrc.py
if [ $? -ne 0 ]; then
	echo "Failed to install mysql-apt-config_0.8.36-1_all.deb. Exiting with code 1"
	exit 1
fi;

sudo apt update
sudo debconf-set-selections <<< "mysql-community-server mysql-community-server/root-pass password $ROOT_PASSWORD"
sudo debconf-set-selections <<< "mysql-community-server mysql-community-server/re-root-pass password $ROOT_PASSWORD"
sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-server
}


mysql_configure () {
# Part 3 - Configure MySQL
# sudo mysql_secure_install
# https://lowendbox.com/blog/automating-mysql_secure_installation-in-mariadb-setup/
echo "Configuring mysql..."
sleep 3

cat <<EOF > config_mysql.py
import pexpect
import os
child = pexpect.spawn('mysql -su root -p')
child.expect('password')
child.sendline(os.getenv("ROOT_PASSWORD"))
f = open('secmysql.sql', 'r')
sql_statements = f.read()
f.close()
sql_statements = sql_statements.replace('MYSQL_PASSWORD', os.getenv("MYSQL_PASSWORD"))
sql_statements = sql_statements.replace('MYSQL_USER', os.getenv("MYSQL_USER"))
child.expect('mysql')
child.sendline(sql_statements)
child.wait()
EOF

python3 config_mysql.py
if [ $? -ne 0 ]; then
	echo "Failed to configure mysql. Exiting with code 1"
	exit 1
fi;
}


database_setup () {
# Part 4 - Setting up database
echo "Setting database up..."
sleep 3

cat <<EOF > setup_db.py
import pexpect
import os
child = pexpect.spawn(f'mysql -u MYSQL_USER -p'.replace('MYSQL_USER', os.getenv('MYSQL_USER')))
child.expect('password')
child.sendline(os.getenv('MYSQL_PASSWORD'))
f = open('database.sql', 'r')
sql_statements = f.read()
f.close()
child.expect('mysql')
child.sendline(sql_statements)
child.sendline('exit')
child.wait()
EOF

python3 setup_db.py
if [ $? -ne 0 ]; then
	echo "Failed to setup sol_db. Exiting with code 1"
	exit 1
fi;
}


project_setup () {
# Part 5 - Setup project
echo "Setting environment up..."
sleep 3

python3 -m venv ./env

./env/bin/pip install -r requirements.txt
if [ $? -ne 0 ]; then
	echo "Failed to install solidaridad requirements. Exiting with code 1"
	exit 1
fi;
./env/bin/pip install waitress

echo "You might need to setup 'MYSQL_HOST' 'PHOTOS_DIR' environment variables"
echo "  Start the project with 'nohup ./env/bin/waitress-serve --call routes:create_app &'"
}



if [ -z "$ROOT_PASSWORD" ]; then
	echo "You need to set 'ROOT_PASSWORD' environment variable"
	exit 1
fi;

if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ]; then
	echo "You need to set 'MYSQL_USER' and 'MYSQL_PASSWORD' environment variables"
	exit 1
fi;

echo "This script requires super user privileges"
sudo ls > /dev/null

operation=${1:-1}  # Default to 1 if no argument is provided
stop=${2:-6}  # Default to 1 if no argument is provided

if [ $operation -eq 0 ]; then
	clone
	if [ $operation -eq $stop ]; then
		exit 0
	fi;
	operation=$((operation+1))
fi;

if [ $operation -eq 1 ]; then
	dependency_install
	if [ $operation -eq $stop ]; then
		exit 0
	fi;
	operation=$((operation+1))
fi;

if [ $operation -eq 2 ]; then
	mysql_install
	if [ $operation -eq $stop ]; then
		exit 0
	fi;
	operation=$((operation+1))
fi;

if [ $operation -eq 3 ]; then
	mysql_configure
	if [ $operation -eq $stop ]; then
		exit 0
	fi;
	operation=$((operation+1))
fi;

if [ $operation -eq 4 ]; then
	database_setup
	if [ $operation -eq $stop ]; then
		exit 0
	fi;
	operation=$((operation+1))
fi;

if [ $operation -eq 5 ]; then
	project_setup
fi;
