import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox, CheckButtons
import tkinter as tk
from tkinter import messagebox

h = 6.62607015e-34
c = 299792458.0
k = 1.380649e-23
b_wien = 2.897771955e-3  # Wien's displacement law constant (m·K)

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
    
    return B_planck, B_rj

def calculate_y_limits(B_planck, B_rj, use_log_scale):
    """
    Calculate appropriate y-axis limits for linear and logarithmic scales.
    
    Y-AXIS SCALING: Limits are defined entirely by Planck's law, not Rayleigh-Jeans.
    No data is rescaled, normalised, or clipped.
    
    Linear scale: Fixed upper limit (8× Planck peak) causes Rayleigh-Jeans to exceed 
    the plot range at short wavelengths, visibly demonstrating classical theory failure.
    
    Log scale: Explicit fixed bounds show true divergence of R-J as λ→0 while keeping
    negligible Planck tail values below the plot floor.
    """
    if use_log_scale:
        # Log scale: explicit fixed bounds (no auto-scaling)
        # Lower bound: exclude numerically negligible Planck tail values
        planck_peak = np.max(B_planck)
        y_lower = 1e-4 * planck_peak
        # Upper bound: allow R-J to grow strongly but remain viewable
        y_upper = 2.0 * np.max(B_rj[:100])
        return y_lower, y_upper
    else:
        # Linear scale: fixed upper limit proportional to Planck peak
        # Rayleigh-Jeans exceeds this range at short wavelengths (classical physics fails)
        planck_peak = np.max(B_planck)
        y_lower = 0.0
        y_upper = 8.0 * planck_peak  # 8× Planck peak forces R-J off the top
        return y_lower, y_upper

# Create figure and main plot area
fig, ax = plt.subplots(figsize=(10, 7))
plt.subplots_adjust(bottom=0.35)

# Initial plot
T_init = 5000.0
B_planck, B_rj = calculate_spectra(T_init)

line_planck, = ax.plot(wavelengths_nm, B_planck, color="black", lw=2, label="Planck Radiation Formula")
line_rj, = ax.plot(wavelengths_nm, B_rj, color="black", ls="--", lw=2, label="Rayleigh–Jeans Law")

ax.axvspan(380, 750, color="royalblue", alpha=0.2, label="Visible range")

ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Spectral Radiance B_λ (W m⁻³ sr⁻¹)")
ax.set_title(f"Classical Rayleigh–Jeans law diverges at short wavelengths; Planck's law remains finite (T = {T_init:.0f} K)")
ax.legend(loc="upper right")
ax.grid(True, ls=":", lw=0.7)

ax.set_xlim(0, 3000)

# Global state for tracking current scale mode (used to apply correct axis limits)
current_use_log_scale = False

# Apply initial y-axis limits for linear scale
y_lower, y_upper = calculate_y_limits(B_planck, B_rj, current_use_log_scale)
ax.set_ylim(y_lower, y_upper)

# Add Wien's displacement law line (updates dynamically with temperature)
wien_lambda_nm = (b_wien / T_init) * 1e9  # Convert m to nm
wien_line = ax.axvline(wien_lambda_nm, color="red", ls="--", lw=1.5, 
                        label=f"Wien peak (λ_max = {wien_lambda_nm:.0f} nm)")

# Add annotation explaining Rayleigh-Jeans divergence
textstr = "Rayleigh-Jeans law:\n• No UV cutoff\n• Diverges as λ→0"
ax.text(0.98, 0.35, textstr, transform=ax.transAxes, fontsize=9,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Create slider
ax_slider = plt.axes([0.2, 0.22, 0.6, 0.03])
slider = Slider(ax_slider, "Temperature (K)", 1000, 10000, valinit=T_init, valstep=100)

# Create reset button
ax_reset = plt.axes([0.2, 0.12, 0.08, 0.05])
btn_reset = Button(ax_reset, 'Reset')

# Create text box for direct input
ax_textbox = plt.axes([0.2, 0.03, 0.1, 0.04])
textbox = TextBox(ax_textbox, 'T (K):', initial='5000')

# Create checkbutton for log scale toggle
ax_log_check = plt.axes([0.65, 0.12, 0.15, 0.05])
log_check = CheckButtons(ax_log_check, ['Log Scale'], [False])

def update(val):
    """Update the plot when the slider changes."""
    T = slider.val
    B_planck, B_rj = calculate_spectra(T)
    
    line_planck.set_ydata(B_planck)
    line_rj.set_ydata(B_rj)
    
    # Reapply y-axis limits when temperature changes (axis limits depend on current data)
    y_lower, y_upper = calculate_y_limits(B_planck, B_rj, current_use_log_scale)
    ax.set_ylim(y_lower, y_upper)
    
    # Update Wien's displacement law line position and label
    wien_lambda_nm = (b_wien / T) * 1e9  # Convert m to nm
    wien_line.set_xdata([wien_lambda_nm, wien_lambda_nm])
    wien_line.set_label(f"Wien peak (λ_max = {wien_lambda_nm:.0f} nm)")
    ax.legend(loc="upper right")
    
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

def on_log_scale_toggle(label):
    """Toggle between linear and logarithmic scale with appropriate axis limits."""
    global current_use_log_scale
    if label == "Log Scale":
        is_log = log_check.get_status()[0]
        current_use_log_scale = is_log
        
        # Change the scale
        if is_log:
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')
        
        # Recalculate and apply appropriate y-axis limits for the new scale
        T = slider.val
        B_planck, B_rj = calculate_spectra(T)
        y_lower, y_upper = calculate_y_limits(B_planck, B_rj, is_log)
        ax.set_ylim(y_lower, y_upper)
        
        fig.canvas.draw_idle()

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
log_check.on_clicked(on_log_scale_toggle)

# Make legend clickable
legend = ax.legend(loc="upper right")
legend_line_map = {}
for legline, origline in zip(legend.get_lines(), [line_planck, line_rj]):
    legline.set_picker(5)
    legend_line_map[legline] = origline

fig.canvas.mpl_connect('pick_event', on_legend_pick)

plt.show()