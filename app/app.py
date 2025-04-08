import pytz
from flask import Flask, render_template, request
import fastf1
import fastf1.plotting
from fastf1.plotting import team_color
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
import os

# HEX COLORS
BACKGROUND = '#232323'
FOREGROUND = '#C7C7C7'

# Dynamic port config for Render
port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

# Enable FastF1 cache
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache('cache')

@app.route('/', methods=['GET', 'POST'])
def index():
    # Load the GPs of the 2025
    schedule = fastf1.get_event_schedule(2025)
    now = datetime.now(pytz.UTC)

    # Create event list
    gps = []
    for _, event in schedule.iterrows():
        event_date = event['Session5Date'].replace(tzinfo=pytz.UTC)
        has_happened = event_date < now

        gps.append({
            "name": event['EventName'],
            "round": event['RoundNumber'],
            "has_happened": has_happened,
        })

    selected_gp = int(request.form.get("selected_gp", gps[1]["round"]))

    # Load data of selected GP of the season 2025
    session = fastf1.get_session(2025, selected_gp, 'R')
    try:
        session.load()
    except ValueError as e:
        if 'testing' in str(e):
            return render_template("error.html", message="L'evento selezionato non è una gara.")

    # Starting grid for the gp
    starting_grid = session.results[['GridPosition', 'DriverNumber', 'Abbreviation', 'TeamName']]
    starting_grid['GridPosition'] = starting_grid['GridPosition'].apply(int)

    # GP Highlights
    fastest_lap = session.laps.pick_fastest()

    # Final results
    final_standings = session.results[['ClassifiedPosition', 'DriverNumber', 'Abbreviation', 'TeamName', 'Points']]
    final_standings['Points'] = final_standings['Points'].apply(int)

    if starting_grid.empty or final_standings.empty:
        print("Starting grid or final standings are empty")
        return render_template("error.html", message="No data available for this race.")

    return render_template("index.html",
                           gps=gps,
                           selected_gp=selected_gp,
                           starting_grid=starting_grid,
                           fastest_lap=fastest_lap,
                           final_standings=final_standings)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)


 # # Get pilots list
 #    drivers = {drv: session.get_driver(drv)['Abbreviation'] for drv in session.drivers}
 #
 #    # Set the selected pilot, if none use the first
 #    selected_driver = request.form.get('driver', list(drivers.keys())[0])
 #    # Get pilot's name
 #    driver_info = session.get_driver(selected_driver)
 #    driver_name = driver_info['FullName']
 #    team_name = driver_info['TeamName']
 #    team_hex_color = team_color(team_name)
 #
 #
 #    # Get datas of the selected pilot
 #    laps_driver = session.laps.pick_driver(selected_driver)
 #    lap_times = laps_driver[["LapNumber", "LapTime"]].dropna()
 #
 #    # Convert lap time in seconds
 #    lap_times["LapTime (s)"] = lap_times["LapTime"].dt.total_seconds()
 #
 #    fig, ax = plt.subplots()
 #    ax.plot(lap_times["LapNumber"], lap_times["LapTime (s)"], marker='o', color=team_hex_color)
 #    ax.set_title(f"Lap times - {driver_name}", color=FOREGROUND)
 #    ax.set_xlabel("Lap")
 #    ax.set_ylabel("Time (s)")
 #    ax.grid(True, linestyle='--', alpha=0.3)
 #    fig.patch.set_facecolor(BACKGROUND)
 #    ax.set_facecolor(BACKGROUND)
 #    ax.tick_params(colors=FOREGROUND)
 #    ax.xaxis.label.set_color(FOREGROUND)
 #    ax.yaxis.label.set_color(FOREGROUND)
 #    ax.title.set_color(FOREGROUND)
 #
 #    # Save the graph as base64 image
 #    buf = io.BytesIO()
 #    plt.tight_layout()
 #    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
 #    buf.seek(0)
 #    plot_laptimes = base64.b64encode(buf.read()).decode("utf-8")
 #    plt.close(fig)
 #
 #    # Rendering page with data and graph
 #    return render_template('index.html',
 #                           gps=gps,
 #                           selected_gp=selected_gp,
 #                           drivers=drivers,
 #                           selected_driver=selected_driver,
 #                           plot_laptimes=plot_laptimes)