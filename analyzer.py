import re
import argparse
from collections import defaultdict
import subprocess
import json
import time
from datetime import datetime

# Cores

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

# Dados

failed_logins = defaultdict(int)
invalid_users = defaultdict(int)
timestamps = defaultdict(list)

# Banner

def banner():
    print(f"""
{Colors.BLUE}
========================================
        SOC LOG MONITOR
========================================
{Colors.RESET}
""")

# Processamento de linha

def process_line(line):
    global last_alert

    # Falha de login
    if "Failed password" in line:
        ip_match = re.search(r'from (\S+)', line)
        user_match = re.search(r'for (\S+)', line)

        if ip_match:
            ip = ip_match.group(1)
            failed_logins[ip] += 1
            timestamps[ip].append(time.time())

            # ALERTA brute force
            if failed_logins[ip] >= 3:
                print(f"{Colors.RED}[ALERTA]{Colors.RESET} Brute force do IP {ip} ({failed_logins[ip]} tentativas)")

            # ALERTA comportamento rￃﾡpido (ataque em curto tempo)
            if len(timestamps[ip]) >= 5:
                if timestamps[ip][-1] - timestamps[ip][0] < 10:
                    print(f"{Colors.RED}[CRￃﾍTICO]{Colors.RESET} Ataque rￃﾡpido detectado do IP {ip}")

        if user_match:
            user = user_match.group(1)
            if "invalid" in line.lower():
                invalid_users[user] += 1

    # Usuￃﾡrio invￃﾡlido
    if "Invalid user" in line:
        user_match = re.search(r'Invalid user (\S+)', line)
        ip_match = re.search(r'from (\S+)', line)

        if user_match and ip_match:
            user = user_match.group(1)
            ip = ip_match.group(1)

            print(f"{Colors.YELLOW}[SUSPEITO]{Colors.RESET} Usuￃﾡrio invￃﾡlido '{user}' do IP {ip}")

    # ALERTA mￃﾺltiplos IPs (ataque distribuￃﾭdo)
    if len(failed_logins) >= 3 and not distributed_alerted:
        print(f"{Colors.RED}[CRￃﾍTICO]{Colors.RESET} Possￃﾭvel ataque distribuￃﾭdo detectado!")
        distributed_alerted = True

# Analisar arquivo

def analyze_file(file_path):
    banner()
    print(f"{Colors.GREEN}[+] Analisando arquivo...{Colors.RESET}\n")

    with open(file_path, 'r') as file:
        for line in file:
            process_line(line)

    summary()

# Monitorar tempo real

def analyze_live():
    banner()
    print(f"{Colors.GREEN}[+] Monitorando em tempo real...{Colors.RESET}\n")

    process = subprocess.Popen(
        ["journalctl", "-u", "ssh", "-f"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in process.stdout:
        process_line(line)
        
# Resumo final

def summary():
    print(f"\n{Colors.BLUE}========== RESUMO =========={Colors.RESET}")

    for ip, count in failed_logins.items():
        print(f"{Colors.RED}IP {ip}: {count} tentativas falhas{Colors.RESET}")

    if not failed_logins:
        print(f"{Colors.GREEN}Nenhuma atividade suspeita detectada.{Colors.RESET}")

# Exportar relatￃﾳrio

def export_report():
    report = {
        "generated_at": str(datetime.now()),
        "failed_logins": dict(failed_logins),
        "invalid_users": dict(invalid_users)
    }

    with open("report.json", "w") as f:
        json.dump(report, f, indent=4)

    print(f"{Colors.BLUE}[+] Relatￃﾳrio exportado para report.json{Colors.RESET}")

# Main

def main():
    parser = argparse.ArgumentParser(description="SOC Log Monitor")
    parser.add_argument("--file", help="Analisar arquivo de log")
    parser.add_argument("--live", action="store_true", help="Monitorar em tempo real")
    parser.add_argument("--export", action="store_true", help="Exportar relatￃﾳrio JSON")

    args = parser.parse_args()

    if args.file:
        analyze_file(args.file)
    elif args.live:
        analyze_live()
    else:
        print("Use --file <arquivo> ou --live")

    if args.export:
        export_report()

if __name__ == "__main__":
    main()
