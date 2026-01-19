import numpy as np
import matplotlib.pyplot as plt

h = 6.62607015e-34
c = 299792458.0
k = 1.380649e-23

T = 5000.0

wavelengths_nm = np.linspace(1, 3000, 1000)
wavelengths_m = wavelengths_nm * 1e-9

x = h * c / (wavelengths_m * k * T)
x = np.clip(x, None, 700)  
exp_term = np.expm1(x)
B_planck = (2 * h * c**2) / (wavelengths_m**5 * exp_term)

#exp_term = np.expm1(h * c / (wavelengths_m * k * T))
#B_planck = (2 * h * c**2) / (wavelengths_m**5 * exp_term)

B_rj = (2 * c * k * T) / (wavelengths_m**4)

B_planck /= np.max(B_planck)

ref_index = np.argmin(np.abs(wavelengths_nm - 1000))
scale_factor = B_planck[ref_index] / B_rj[ref_index]
B_rj_scaled = B_rj * scale_factor

plt.figure(figsize=(9,6))
plt.plot(wavelengths_nm, B_planck, color="black", lw=2, label="Planck Radiation Formula")
plt.plot(wavelengths_nm, B_rj_scaled, color="black", ls="--", lw=2, label="Rayleigh–Jeans Law")

plt.axvspan(380, 750, color="royalblue", alpha=0.2, label="Visible range")

plt.xlabel("Wavelength (nm)")
plt.ylabel("Relative Intensity (arbitrary units)")
plt.title("Ultraviolet Catastrophe vs Planck's Law (T = 5000 K)")
plt.legend()
plt.grid(True, ls=":", lw=0.7)

plt.xlim(0, 3000)
plt.ylim(0, 1.2)

plt.tight_layout()
plt.show()