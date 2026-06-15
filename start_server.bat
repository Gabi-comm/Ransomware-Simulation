@echo off
echo Starting local web server on port 8000...
echo Phone QR code will point to: http://192.168.1.16:8000/www/index.html
python -m http.server 8000
pause
