import re
import argparse
from collections import defaultdict
import subprocess

failed_logins = defaultdict(int)
invalid_users = defaultdict(int)

def process_line(line):
    # Detectar falha de login
    if "Failed password" in line:
        ip_match = re.search(r'from (\S+)', line)
        user_match = re.search(r'for (\S+)', line)

        if ip_match:
            ip = ip_match.group(1)
            failed_logins[ip] += 1

            if failed_logins[ip] >= 3:
                print(f"[ALERTA] Possível brute force do IP {ip} ({failed_logins[ip]} tentativas)")

        if user_match:
            user = user_match.group(1)
            if user == "invalid":
                invalid_users[user] += 1

    # Detectar usuário inválido
    if "Invalid user" in line:
        user_match = re.search(r'Invalid user (\S+)', line)
        ip_match = re.search(r'from (\S+)', line)

        if user_match and ip_match:
            user = user_match.group(1)
            ip = ip_match.group(1)

            print(f"[ALERTA] Tentativa com usuário inválido '{user}' do IP {ip}")

def analyze_file(file_path):
    print("\n[+] Analisando arquivo de logs...\n")

    with open(file_path, 'r') as file:
        for line in file:
            process_line(line)

def analyze_live():
    print("\n[+] Monitorando logs em tempo real...\n")

    process = subprocess.Popen(
        ["journalctl", "-u", "ssh", "-f"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in process.stdout:
        process_line(line)

def main():
    parser = argparse.ArgumentParser(description="SOC Log Analyzer")
    parser.add_argument("--file", help="Analisar arquivo de log")
    parser.add_argument("--live", action="store_true", help="Monitorar logs em tempo real")

    args = parser.parse_args()

    if args.file:
        analyze_file(args.file)
    elif args.live:
        analyze_live()
    else:
        print("Use --file <arquivo> ou --live")

if __name__ == "__main__":
    main()
