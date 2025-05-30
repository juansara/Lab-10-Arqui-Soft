from metrics import check_latency, check_availability, render_graph

def run_bot():
    print("MonitorMach CLI - Escribe un comando. Usa 'exit' para salir.")

    while True:
        cmd = input("> ").strip()
        if cmd.lower() in ["exit", "salir", "quit"]:
            break

        try:
            if cmd.startswith("CheckLatency"):
                _, mod, start, end = cmd.split()
                check_latency(mod, start, end)

            elif cmd.startswith("CheckAvailability"):
                _, mod, period = cmd.split()
                check_availability(mod, period)

            elif cmd.startswith("RenderGraph"):
                _, metric, period = cmd.split()
                render_graph(metric, period)

            else:
                print("Comando no reconocido.")
        except Exception as e:
            print(f"Error ejecutando comando: {e}")

if __name__ == "__main__":
    run_bot()
