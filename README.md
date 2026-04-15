# 🔐 SOC Log Monitor

Ferramenta em Python para análise e monitoramento de logs SSH em ambiente Linux.

## 🚀 Funcionalidades

- 🔴 Detecção de brute force (múltiplas tentativas de login)
- 🟡 Identificação de usuários inválidos
- 🟢 Monitoramento em tempo real (journalctl)
- 📊 Resumo de atividades suspeitas

## 🛠️ Tecnologias

- Python
- Linux
- Regex
- Journalctl

🎯 Objetivo

Simular atividades de um analista SOC (Blue Team), identificando e respondendo a eventos suspeitos em logs de autenticação.

📈 Aprendizados
-Análise de logs reais
-Detecção de ataques de força bruta
-Monitoramento de segurança em tempo real
-Automação com Python

📷 Demonstração

![Demo](screenshot.jog)

## ▶️ Como usar

### Analisar arquivo:
```bash
python3 analyzer.py --file logs.txt
```
Monitorar em tempo real:
```bash
sudo python3 analyzer.py --live
```
📌 Exemplo de saída
```bash
[ALERTA] Possível brute force do IP ::1 (5 tentativas)
[ALERTA] Tentativa com usuário inválido 'admin' do IP 192.168.0.10
```
👨‍💻 Autor
Gustavo Matias Silva
