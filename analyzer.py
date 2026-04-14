import re
import argparse
from collections import defaultdict
import subprocess

# Cores no terminal
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

failed_logins = defaultdict(int)
invalid_users = defaultdict(int)

def banner():
    print(f"""
{Colors.BLUE}
========================================
        SOC LOG MONITOR
========================================
{Colors.RESET}
""")

def process_line(line):
    # Falha de login
    if "Failed password" in line:
        ip_match = re.search(r'from (\S+)', line)
        user_match = re.search(r'for (\S+)', line)

        if ip_match:
            ip = ip_match.group(1)
            failed_logins[ip] += 1

            if failed_logins[ip] >= 3:
                print(f"{Colors.RED}[ALERTA]{Colors.RESET} Brute force do IP {ip} ({failed_logins[ip]} tentativas)")

        if user_match:
            user = user_match.group(1)
            if user == "invalid":
                invalid_users[user] += 1

    # Usuário inválido
    if "Invalid user" in line:
        user_match = re.search(r'Invalid user (\S+)', line)
        ip_match = re.search(r'from (\S+)', line)

        if user_match and ip_match:
            user = user_match.group(1)
            ip = ip_match.group(1)

            print(f"{Colors.YELLOW}[SUSPEITO]{Colors.RESET} Usuário inválido '{user}' do IP {ip}")

def analyze_file(file_path):
    banner()
    print(f"{Colors.GREEN}[+] Analisando arquivo...{Colors.RESET}\n")

    with open(file_path, 'r') as file:
        for line in file:
            process_line(line)

    summary()

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

def summary():
    print(f"\n{Colors.BLUE}========== RESUMO =========={Colors.RESET}")

    for ip, count in failed_logins.items():
        print(f"{Colors.RED}IP {ip}: {count} tentativas falhas{Colors.RESET}")

    if not failed_logins:
        print(f"{Colors.GREEN}Nenhuma atividade suspeita detectada.{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description="SOC Log Monitor")
    parser.add_argument("--file", help="Analisar arquivo de log")
    parser.add_argument("--live", action="store_true", help="Monitorar em tempo real")

    args = parser.parse_args()

    if args.file:
        analyze_file(args.file)
    elif args.live:
        analyze_live()
    else:
        print("Use --file <arquivo> ou --live")

if __name__ == "__main__":
    main()
