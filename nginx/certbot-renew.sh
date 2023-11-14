#!/bin/sh
certbot renew --nginx --quiet
nginx -s reload
