import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
import tkinter as tk
from tkinter import messagebox

h = 6.62607015e-34
c = 299792458.0
k = 1.380649e-23

# Pre-calculate wavelengths (constant)
wavelengths_nm = np.linspace(1, 3000, 1000)
wavelengths_m = wavelengths_nm * 1e-9

def calculate_spectra(T):
    """Calculate Planck and Rayleigh-Jeans spectra for a given temperature."""
    x = h * c / (wavelengths_m * k * T)
    x = np.clip(x, None, 700)  
    exp_term = np.expm1(x)
    B_planck = (2 * h * c**2) / (wavelengths_m**5 * exp_term)
    
    B_rj = (2 * c * k * T) / (wavelengths_m**4)
    
    B_planck /= np.max(B_planck)
    
    ref_index = np.argmin(np.abs(wavelengths_nm - 1000))
    scale_factor = B_planck[ref_index] / B_rj[ref_index]
    B_rj_scaled = B_rj * scale_factor
    
    return B_planck, B_rj_scaled

# Create figure and main plot area
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.35)

# Initial plot
T_init = 5000.0
B_planck, B_rj_scaled = calculate_spectra(T_init)

line_planck, = ax.plot(wavelengths_nm, B_planck, color="black", lw=2, label="Planck Radiation Formula")
line_rj, = ax.plot(wavelengths_nm, B_rj_scaled, color="black", ls="--", lw=2, label="Rayleigh–Jeans Law")

ax.axvspan(380, 750, color="royalblue", alpha=0.2, label="Visible range")

ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Relative Intensity (arbitrary units)")
ax.set_title(f"Ultraviolet Catastrophe vs Planck's Law (T = {T_init:.0f} K)")
ax.legend(loc="upper right")
ax.grid(True, ls=":", lw=0.7)

ax.set_xlim(0, 3000)
ax.set_ylim(0, 1.2)

# Create slider
ax_slider = plt.axes([0.2, 0.22, 0.6, 0.03])
slider = Slider(ax_slider, "Temperature (K)", 1000, 10000, valinit=T_init, valstep=100)

# Create reset button
ax_reset = plt.axes([0.2, 0.12, 0.08, 0.05])
btn_reset = Button(ax_reset, 'Reset')

# Create text box for direct input
ax_textbox = plt.axes([0.2, 0.03, 0.1, 0.04])
textbox = TextBox(ax_textbox, 'T (K):', initial='5000')

def update(val):
    """Update the plot when the slider changes."""
    T = slider.val
    B_planck, B_rj_scaled = calculate_spectra(T)
    
    line_planck.set_ydata(B_planck)
    line_rj.set_ydata(B_rj_scaled)
    
    ax.set_title(f"Ultraviolet Catastrophe vs Planck's Law (T = {T:.0f} K)")
    textbox.set_val(f'{T:.0f}')
    
    fig.canvas.draw_idle()

def reset(event):
    """Reset temperature to 5000 K."""
    slider.set_val(5000.0)

def on_text_submit(text):
    """Handle temperature input from text box."""
    try:
        T = float(text)
        if 1000 <= T <= 10000:
            slider.set_val(T)
        else:
            print("Temperature must be between 1000 and 10000 K")
            textbox.set_val(f'{slider.val:.0f}')
    except ValueError:
        print("Invalid temperature value")
        textbox.set_val(f'{slider.val:.0f}')

def on_pick(event):
    """Show formula when clicking on legend items."""
    if event.artist == line_planck:
        formula = "Planck Radiation Formula:\n\nB(λ,T) = (2hc²/λ⁵) × 1/(e^(hc/λkT) - 1)\n\nwhere:\nh = Planck's constant\nc = speed of light\nλ = wavelength\nk = Boltzmann constant\nT = temperature"
        messagebox.showinfo("Planck Radiation Formula", formula)
    elif event.artist == line_rj:
        formula = "Rayleigh-Jeans Law:\n\nB(λ,T) = (2ckT/λ⁴)\n\nwhere:\nc = speed of light\nk = Boltzmann constant\nT = temperature\nλ = wavelength"
        messagebox.showinfo("Rayleigh-Jeans Law", formula)

def on_legend_pick(event):
    """Show formula when clicking on legend text."""
    legline = event.artist
    origline = legend_line_map.get(legline)
    if origline == line_planck:
        formula = "Planck Radiation Formula:\n\nB(λ,T) = (2hc²/λ⁵) × 1/(e^(hc/λkT) - 1)\n\nwhere:\nh = Planck's constant\nc = speed of light\nλ = wavelength\nk = Boltzmann constant\nT = temperature"
        messagebox.showinfo("Planck Radiation Formula", formula)
    elif origline == line_rj:
        formula = "Rayleigh-Jeans Law:\n\nB(λ,T) = (2ckT/λ⁴)\n\nwhere:\nc = speed of light\nk = Boltzmann constant\nT = temperature\nλ = wavelength"
        messagebox.showinfo("Rayleigh-Jeans Law", formula)

slider.on_changed(update)
btn_reset.on_clicked(reset)
textbox.on_submit(on_text_submit)

# Make legend clickable
legend = ax.legend(loc="upper right")
legend_line_map = {}
for legline, origline in zip(legend.get_lines(), [line_planck, line_rj]):
    legline.set_picker(5)
    legend_line_map[legline] = origline

fig.canvas.mpl_connect('pick_event', on_legend_pick)

plt.show()