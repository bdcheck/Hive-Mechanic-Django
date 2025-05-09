#!/bin/bash

echo "Cleaning lock files..."

rm /tmp/*.lock

echo "Configuring e-mail server..."

echo "root=$CRON_MAIL_RECIPIENT" > /etc/ssmtp/ssmtp.conf
echo "mailhub=$CRON_MAIL_SERVER" >> /etc/ssmtp/ssmtp.conf
echo "rewriteDomain=$CRON_MAIL_DOMAIN" >> /etc/ssmtp/ssmtp.conf
echo "hostname=$CRON_SENDER_HOSTNAME" >> /etc/ssmtp/ssmtp.conf
echo "UseTLS=Yes" >> /etc/ssmtp/ssmtp.conf
echo "UseSTARTTLS=Yes" >> /etc/ssmtp/ssmtp.conf
echo "FromLineOverride=Yes" >> /etc/ssmtp/ssmtp.conf
echo "AuthUser=$CRON_MAIL_USERNAME" >> /etc/ssmtp/ssmtp.conf
echo "AuthPass=$CRON_MAIL_PASSWORD" >> /etc/ssmtp/ssmtp.conf

echo "Updating CRON configuration..."

sed -i s/CRON_MAIL_RECIPIENT/"$CRON_MAIL_RECIPIENT"/g /etc/cron.d/django
sed -i s/CRON_FROM_EMAIL/"$CRON_FROM_EMAIL"/g /etc/cron.d/django

echo "Starting CRON..."

cron && tail -f /var/log/cron.log
