#!/bin/bash -xe
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
sudo yum update -y
sudo sleep 20
sudo yum -y install httpd python3-mod_wsgi git zsh
usermod -a -G apache ec2-user
sudo git clone https://github.com/malbertus/basic_web_app.git /var/www/basic_web_app
sudo pip3 install -r /var/www/basic_web_app/requirements.txt
sudo mv /var/www/basic_web_app/apache.conf /etc/httpd/conf.d/basic_web_app.conf
sudo chown -R ec2-user:apache /var/www/basic_web_app
export APPENV=environment
export APPNAME=app_name
export APPDNS=alb_dns
export FLASK_ENV=development
export FLASK_APP=app.py
sudo systemctl enable httpd.service
sudo systemctl start httpd.service
cat > /etc/profile.d/load_env.sh << 'EOF'
export APPENV=environment
export APPNAME=app_name
export APPDNS=alb_dns
export FLASK_ENV=development
export FLASK_APP=app.py
EOF