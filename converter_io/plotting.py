import matplotlib.pyplot as plt
from astropy.time import Time
from utils import angle_converter as ac
from utils import date_converter as dc

import numpy as np
def show_polar_plot(values: list, config_name: str, draw_lines=False):
    plt.style.use("_mpl-gallery")
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    angles = []
    radii = []
    colors = []
    for (i, (time, era, az, el)) in enumerate(values):
        radius: float = 90 - el
        angle: float = ac.deg_to_rad(az)
        color = [0, 0, i / len(values)]
        angles.append(angle)
        radii.append(radius)
        colors.append(color)

    times = np.linspace(0, 10, len(angles))

    if draw_lines:
        ax.plot(angles, radii)
    else:
        ax.scatter(angles, radii, c=times, cmap='viridis')
    time_start: Time = Time(values[0][0], format="jd")
    time_start.format = "iso"
    time_end: Time = Time(values[-1][0], format="jd")
    time_end.format = "iso"
    ax.set_rticks([45, 90, 135, 180])
    ax.grid(True)
    plt.text(-0.30, 0.10,
             f"Plotting {config_name}\nfrom: {time_start}\nto:   {time_end}",
             transform=plt.gca().transAxes, fontsize=12,
             verticalalignment='bottom', horizontalalignment='left')
    plt.subplots_adjust(left=0.05, bottom=0.05, top=0.95)
    plt.show()


def show_simple_plot(values: list, config_name: str, detailed=False):
    plt.style.use("_mpl-gallery")
    fig, ax = plt.subplots()
    t = []
    y1 = []
    y2 = []
    for (time, era, az, el) in values:
        t.append(dc.hours_from_julian_days(time))
        y1.append(az)
        y2.append(el)
    ax.scatter(t, y1, label="Azimuth", color="lime")
    ax.scatter(t, y2, label="Elevation", color="royalblue")
    ax.set(xlabel='time [hours]', ylabel='Azimuth and Elevation [degrees]',
           title='Azimuth and Elevation plotted against time')
    plt.subplots_adjust(left=0.05, bottom=0.05, top=0.925)
    time_start: Time = Time(values[0][0], format="jd")
    time_start.format = "iso"
    time_end: Time = Time(values[-1][0], format="jd")
    time_end.format = "iso"
    ax.set_title(f"Plotting {config_name}\nfrom: {time_start}\nto:   {time_end}")
    ax.grid(True)
    ax.set_yticks([-90, -45, 0, 45, 90, 135, 180, 225, 270, 315, 360])
    ax.axhline(y=360, color="lime", alpha=0.5)
    ax.axhline(y=-90, color="royalblue", alpha=0.5)
    if detailed:
        ax.axhline(y=30, color="royalblue", alpha=0.3)
        plt.plot([6, 6], [30, 90], color="royalblue", alpha=0.3)
        plt.plot([19, 19], [30, 90], color="royalblue", alpha=0.3)
    ax.axhline(y=0, color="lime", alpha=0.5)

    ax.axhline(y=90, color="royalblue", alpha=0.5)
    ax.set_xticks([0, 6, 12, 18, 24])

    ax.legend()
    plt.show()
