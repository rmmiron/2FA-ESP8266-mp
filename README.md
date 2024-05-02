# 2FA-ESP8266-mp
2FA ESP8266 Dongle

Lolin D1 Mini (ESP8266)
MicroPython

Armazena seeds em um arquivo texto e gera códigos TOTP a partir destes seeds, como segundo fator de autenticação.

Exibe um menu em um display OLED de 0.96" SSD1306 com as contas e respectivos códigos OTP.

É necessário criar um arquivo `config.py` no mesmo diretório, contendo ssid e senha para a rede local.
A única função desta conexão é sincronizar o relógio e gerar os códigos TOTP de acordo com a hora.

