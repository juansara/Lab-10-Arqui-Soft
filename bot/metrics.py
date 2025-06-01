import os
import re
from collections import defaultdict
from datetime import datetime, timedelta

LOG_DIR = "logs"

def parse_log(line):
    try:
        parts = line.strip().split("|")
        date = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        module = parts[1]
        status_code = int(parts[3])
        latency = float(parts[4]) * 1000
        return {
            "date": date,
            "module": module,
            "status_code": status_code,
            "latency": latency,
        }
    except:
        return None

def get_log_path(module):
    filename = module.replace(" ", "_").lower() + ".log"

    if filename == "pokeimage.log":
        filename = "poke_images.log"
    elif filename == "pokeapi.log":
        filename = "poke_api.log"
    elif filename == "pokesearch.log":
        filename = "poke_search.log"
    elif filename == "pokestats.log":
        filename = "poke_stats.log"

    return os.path.join(LOG_DIR, filename)

def load_logs(module):
    path = get_log_path(module)
    if not os.path.exists(path):
        print(f"No se encontro el archivo de logs para el modulo {module}.")
        return []
    else:
        with open(path, "r") as file:
            lines = file.readlines()
        return [log for log in (parse_log(line) for line in lines) if log]
    
def format_date(date):
    return date.strftime("%d/%m")

def parse_ddmm(date_str):
    """Convierte dd/mm en datetime con el año actual."""
    day, month = map(int, date_str.strip("-").split("/"))
    year = datetime.now().year
    return datetime(year, month, day)

def get_range_days(end_date, num_days):
    return [(end_date - timedelta(days=i)) for i in reversed(range(num_days))]

def check_latency(module, start, end):
    logs = load_logs(module)
    start_date = parse_ddmm(start).date()
    end_date = parse_ddmm(end).date()

    data_by_day = defaultdict(list)

    for log in logs:
        if start_date <= log["date"].date() <= end_date:
            data_by_day[log["date"].date()].append(log["latency"])

    for i in range((end_date - start_date).days + 1):
        day = start_date + timedelta(days=i)
        values = data_by_day.get(day, [])
        day_str = format_date(day)
        if values:
            avg = int(sum(values) / len(values))
            print(f"{day_str} {avg}ms")
        else:
            print(f"{day_str} No data")

def check_availability(module, period):
    days = int(period.replace("-Last", "").replace("Days", ""))
    logs = load_logs(module)
    end_date = datetime.now().date()
    target_dates = get_range_days(end_date, days)

    daily_status = defaultdict(lambda: {"ok": 0, "total": 0})

    for log in logs:
        if isinstance(log["date"], datetime):
            log_day = log["date"].date()
        else:
            log_day = log["date"]

        if log_day in target_dates:
            daily_status[log_day]["total"] += 1
            if 200 <= log["status_code"] < 300:
                daily_status[log_day]["ok"] += 1

    for day in target_dates:
        stats = daily_status.get(day)
        day_str = format_date(day)
        if stats and stats["total"] > 0:
            pct = (stats["ok"] / stats["total"]) * 100
            print(f"{day_str} {pct:.2f}%")
        else:
            print(f"{day_str} No data")

def render_graph(metric_flag, module, period):
    metric = metric_flag.strip("-")
    days = int(period.replace("-Last", "").replace("Days", ""))
    end_date = datetime.now().date()
    target_dates = get_range_days(end_date, days)
    day_labels = [format_date(day) for day in target_dates]

    logs = load_logs(module)
    daily_values = defaultdict(list)

    for log in logs:
        log_day = log["date"].date()
        if log_day in target_dates:
            if metric.lower() == "latency":
                daily_values[log_day].append(log["latency"])
            elif metric.lower() == "availability":
                daily_values[log_day].append(log["status_code"])

    raw_values = []
    for day in target_dates:
        values = daily_values.get(day, [])
        if not values:
            raw_values.append(None)
        elif metric.lower() == "latency":
            avg = int(sum(values) / len(values))
            raw_values.append(avg)
        elif metric.lower() == "availability":
            ok = len([v for v in values if 200 <= v < 300])
            pct = int((ok / len(values)) * 100)
            raw_values.append(pct)

    if all(v is None for v in raw_values):
        print("No data to render.")
        return

    # Construir una línea por valor, cada uno alineado con su fecha
    lines = []
    ordered = sorted([(i, v) for i, v in enumerate(raw_values) if v is not None], key=lambda x: -x[1])

    for i, val in ordered:
        line = [" " * 10] * len(raw_values)
        line[i] = f"**{val}**".center(10)
        lines.append("".join(line))

    # Imprimir todas las líneas (una por valor)
    for line in lines:
        print(line)

    # Imprimir etiquetas de fechas alineadas
    date_row = ""
    for label in day_labels:
        date_row += f"{label.center(10)}"
    print(date_row)
