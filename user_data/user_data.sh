#!/bin/bash -xe
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
sudo yum update -y
sudo sleep 20
sudo yum -y install httpd python3-mod_wsgi git
sudo pip3 install flask flask-sqlalchemy boto3 python-dotenv pymysql ec2-metadata
usermod -a -G apache ec2-user
sudo git clone https://github.com/malbertus/basic_web_app.git /var/www/basic_web_app
sudo mv /var/www/basic_web_app/apache.conf /etc/httpd/conf.d/basic_web_app.conf
sudo chown -R ec2-user:apache /var/www/basic_web_app
export env=environment
export appname=app_name
export dns=alb_dns
echo $dns
sudo systemctl enable httpd.service
sudo systemctl start httpd.service
cat > /etc/profile.d/load_env.sh << 'EOF'
export env=environment
export appname=app_name
export dns=alb_dns
EOF