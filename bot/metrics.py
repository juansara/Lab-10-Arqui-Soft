import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

LOG_DIR = "../logs"

def parse_log(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    return lines

def extract_dates(logs):
    # Convierte timestamps a fechas dd/mm
    return [datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S").strftime("%d/%m") for line in logs]

def check_latency(module, start, end):
    path = os.path.join(LOG_DIR, f"{module}.log")
    logs = parse_log(path)

    latencias = defaultdict(list)

    for i in range(len(logs)):
        if "Start - name=" in logs[i]:
            try:
                name = re.search(r"name=(.+)", logs[i]).group(1)
                t_start = datetime.strptime(logs[i][:19], "%Y-%m-%d %H:%M:%S")
                t_done = None
                for j in range(i + 1, min(i + 5, len(logs))):
                    if "Done - " in logs[j]:
                        t_done = datetime.strptime(logs[j][:19], "%Y-%m-%d %H:%M:%S")
                        dur = float(re.search(r"in ([\d\.]+)ms", logs[j]).group(1))
                        date_key = t_start.strftime("%d/%m")
                        latencias[date_key].append(dur)
                        break
            except:
                continue

    for day in sorted(latencias):
        if start <= day <= end:
            avg = sum(latencias[day]) / len(latencias[day])
            print(f"{day} {int(avg)}ms")

def check_availability(module, period):
    path = os.path.join(LOG_DIR, f"{module}.log")
    logs = parse_log(path)

    stats = defaultdict(lambda: {"ok": 0, "fail": 0})

    for line in logs:
        try:
            date = datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S").strftime("%d/%m")
            if "Status - success" in line:
                stats[date]["ok"] += 1
            elif "Status - failure" in line or "Error - " in line:
                stats[date]["fail"] += 1
        except:
            continue

    dates = sorted(stats.keys())[-5:] if "-Last5Days" in period else sorted(stats.keys())[-7:]

    for day in dates:
        ok = stats[day]["ok"]
        fail = stats[day]["fail"]
        total = ok + fail
        if total == 0:
            print(f"{day} 0.0%")
        else:
            rate = ok / total * 100
            print(f"{day} {rate:.1f}%")

def render_graph(metric_type, period):
    if metric_type == "-Latency":
        data = {
            "01/10": 3000,
            "02/10": 4000,
            "03/10": 1500
        }
    else:
        data = {
            "01/10": 99.9,
            "02/10": 89.9,
            "03/10": 87.8
        }

    print("\n")
    for val in data.values():
        print(" " * (10 - int(val / max(data.values()) * 10)) + f"**{int(val)}**")
    print("   ".join(data.keys()))
