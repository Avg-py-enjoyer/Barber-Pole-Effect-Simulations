# 🌀 Optical Rotatory Dispersion (ORD) & The Barber Pole Effect

A comprehensive computational optics simulation, theoretical framework, and 3D animation suite for modeling **Optical Rotatory Dispersion (ORD)** and the **Barber Pole Effect** in chiral media (such as aqueous D-glucose solutions).

This repository combines:
1. **Volumetric Raymarching & Physical Colorimetry Engine** (`barber_pole/`): Simulates transverse Rayleigh dipole scattering across discrete laser modes and continuous polychromatic spectra.
2. **Scientific ORD Relationship Analyzer** (`plot_ord_relations.py`): Publication-grade Matplotlib dashboards demonstrating Biot's law, Cauchy dispersion, spatial helical pitch stretching, polarization fanning dials, and analyzer extinction spectra.
3. **Cinematic 3D Mathematical Animations** (`manim_scenes.py`): Five production-ready Manim Community scenes visualizing rotating $\vec{E}$-field vectors, helical wavefront splitting, walking stripes dynamics, and continuous 3D barber pole ribbons inside a transparent cylindrical cell.
4. **Interactive Dashboard & 3D Web Visualizers**: Interactive Qt/Matplotlib parameter sliders and WebGL Plotly 3D interactive helical rays.

---

## 📚 Theoretical Foundations & Context

### 1. Chirality, Optical Activity, and Circular Birefringence

Optical activity occurs in substances that lack improper rotation axes ($S_n$, including inversion centers and mirror planes). Chiral molecules—such as **D-glucose (dextrose)**—interact asymmetrically with circularly polarized electromagnetic waves due to their non-centrosymmetric helical electron clouds.

An arbitrary linearly polarized plane wave propagating along the optical axis ($z$) with initial polarization angle $\theta_0$ can be represented as an equal-amplitude coherent superposition of **Right-Circularly Polarized (RCP, $+$)** and **Left-Circularly Polarized (LCP, $-$)** normal modes:

$$\vec{E}(z=0, t) = \frac{E_0}{\sqrt{2}} \left( \hat{e}_+ e^{i\theta_0} + \hat{e}_- e^{-i\theta_0} \right) e^{-i\omega t}$$

where the circular unit basis vectors are $\hat{e}_\pm = \frac{1}{\sqrt{2}} (\hat{x} \pm i\hat{y})$.

Because the molecular chiral potential couples differently to right- and left-handed helical fields, the medium exhibits **circular birefringence**, meaning the refractive indices for RCP and LCP waves differ slightly:

$$n_R \neq n_L \implies \Delta n = n_L - n_R$$

As the wave propagates a distance $z$ through the chiral solution, the two circular modes accumulate different spatial phase shifts:

$$k_R = \frac{2\pi n_R}{\lambda_0}, \quad k_L = \frac{2\pi n_L}{\lambda_0}$$

$$\vec{E}(z, t) = \frac{E_0}{\sqrt{2}} \left[ \hat{e}_+ e^{i(k_R z - \omega t + \theta_0)} + \hat{e}_- e^{i(k_L z - \omega t - \theta_0)} \right]$$

Factoring out the common propagation phase factor $e^{i \bar{k} z - i\omega t}$ (where $\bar{k} = \frac{k_R + k_L}{2}$):

$$\vec{E}(z, t) = E_0 e^{i(\bar{k} z - \omega t)} \left[ \hat{x} \cos\left( \theta_0 + \frac{\Delta k}{2} z \right) + \hat{y} \sin\left( \theta_0 + \frac{\Delta k}{2} z \right) \right]$$

Thus, the electric field vector remains strictly **linearly polarized**, but its plane of polarization rotates continuously about the propagation axis by an angle $\theta(z)$:

$$\theta(z) = \theta_0 + \rho \cdot z = \theta_0 + \frac{\pi}{\lambda_0}(n_L - n_R) z$$

* **Dextrorotatory ($d$ or $+$)**: $n_L > n_R \implies \theta(z)$ rotates clockwise looking into the oncoming light beam (e.g., D-glucose).
* **Levorotatory ($l$ or $-$)**: $n_R > n_L \implies \theta(z)$ rotates counterclockwise (e.g., D-fructose).

---

### 2. Biot's Law & Specific Rotation

Jean-Baptiste Biot (1815) established empirically that for a dilute solution of chiral molecules dissolved in an optically inactive solvent, the total optical rotation $\theta$ is directly proportional to the solute mass concentration $c$ and the optical path length $z$:

$$\theta(\lambda, T) = [\alpha]_\lambda^T \cdot c \cdot z$$

| Quantity | Symbol | Typical Experimental Units |
|---|---|---|
| Observed optical rotation | $\theta$ | degrees ($^\circ$) or radians |
| Specific rotation | $[\alpha]_\lambda^T$ | $^\circ \cdot \text{dm}^{-1} \cdot (\text{g/cm}^3)^{-1}$ |
| Solute mass concentration | $c$ | $\text{g/cm}^3$ (or $\text{g/mL}$) |
| Optical path length | $z$ | $\text{dm}$ (polarimetry) or $\text{cm}$ (spectrophotometry) |

For D-glucose at the standard Sodium D line ($\lambda = 589.3\text{ nm}$) at $20^\circ\text{C}$, the specific rotation at mutarotational equilibrium is $[\alpha]_D^{20} = +52.7^\circ \text{ dm}^{-1} (\text{g/mL})^{-1}$.

---

### 3. Optical Rotatory Dispersion (ORD) & Cauchy's Formula

The circular birefringence $\Delta n(\lambda) = n_L(\lambda) - n_R(\lambda)$ varies strongly with wavelength. Far away from molecular electronic absorption bands (away from the anomalous **Cotton effect** in the ultraviolet), the dispersion follows **Augustin-Louis Cauchy's normal dispersion law**:

$$\rho(\lambda) = \frac{\theta}{c \cdot z} \approx \frac{A}{\lambda^2} + \frac{B}{\lambda^4} + \dots$$

Retaining the leading-order term yields the governing ORD relation used throughout this project:

$$\theta(z, \lambda) = \theta_0 + \frac{A}{\lambda^2} \cdot c \cdot z$$

where:
* $A \approx 2.1 \times 10^6 \text{ nm}^2 \cdot \text{rad} \cdot \text{cm}^{-1} \cdot (\text{g/cm}^3)^{-1}$ is the Cauchy rotatory parameter for concentrated aqueous glucose.
* $\lambda$ is the vacuum wavelength in nanometers.

#### Physical Consequence of $1/\lambda^2$ Dispersion
Because $\theta \propto 1/\lambda^2$, short-wavelength (violet/blue) light rotates substantially faster than long-wavelength (red) light:

$$\frac{\theta_{\text{violet}}(400\text{ nm})}{\theta_{\text{red}}(700\text{ nm})} = \left( \frac{700}{400} \right)^2 \approx 3.06$$

Violet light undergoes more than **three times** the angular rotation of red light over the exact same propagation distance. When linearly polarized white light enters the solution, its polarization states fan out into a full chromatic circle.

---

### 4. The Barber Pole Effect: Rayleigh Dipole Scattering

When a cylindrical tube containing sugar water is illuminated axially with polarized light, distinct helical rainbow stripes appear on the tube walls when viewed from the side. This is known as the **Barber Pole Effect**.

#### Why Do We See Transverse Stripes?
The visual phenomenon is governed by **Rayleigh scattering** from suspended micro-particles or solvent/solute concentration fluctuations:

1. The incident propagating electric field $\vec{E}(z, \lambda)$ induces an oscillating electric dipole moment in the fluid molecules:
   $$\vec{p}(z, \lambda) = \alpha \vec{E}(z, \lambda)$$
2. An oscillating dipole does **not** radiate along its own oscillation axis ($\vec{p} \parallel \vec{E}$). The scattered radiant intensity $I$ along a unit viewing direction $\hat{n}_{\text{view}}$ is proportional to the square of the transverse acceleration:
   $$I \propto |\vec{p} \times \hat{n}_{\text{view}}|^2 = |\vec{p}|^2 \sin^2(\psi)$$
   where $\psi$ is the angle between the dipole orientation $\vec{p}$ (polarization plane $\theta(z, \lambda)$) and the observer's line of sight $\hat{n}_{\text{view}}$.
3. When viewed horizontally perpendicular to the cylinder axis (viewing angle $\phi_{\text{view}}$ in the transverse plane):
   $$I(z, \lambda) \propto \cos^2\left(\theta(z, \lambda) - \phi_{\text{view}}\right)$$

#### Extinction vs. Maximum Scattering
* **Extinction ($I = 0$)**: Occurs when the electric field vector $\vec{E}(z, \lambda)$ points directly toward the observer's eye ($\theta - \phi_{\text{view}} = \pm 90^\circ$). The oscillating dipoles radiate zero energy along this line of sight.
* **Maximum Intensity ($I = I_{\max}$)**: Occurs when $\vec{E}(z, \lambda)$ oscillates perpendicular to the line of sight ($\theta - \phi_{\text{view}} = 0^\circ \text{ or } 180^\circ$).

---

### 5. Spatial Helical Pitch & Stripe Separation

Because the polarization plane rotates steadily with depth $z$, the locus of maximum scattering traces out a spatial helix winding around the cylinder.

The axial distance required for the polarization vector to execute a full $2\pi$ spatial turn is the **helical pitch** $P(\lambda)$:

$$\Delta\theta = 2\pi \implies \frac{A}{\lambda^2} c \cdot P(\lambda) = 2\pi \implies P(\lambda) = \frac{2\pi \lambda^2}{A \cdot c}$$

Because the dipole scattering intensity $\cos^2(\theta - \phi_{\text{view}})$ has $\pi$-periodicity, the visible bright stripe repeats every half-turn:

$$P_{\text{stripe}}(\lambda) = \frac{\pi \lambda^2}{A \cdot c}$$

#### Wavelength Dependence of Pitch
Since $P \propto \lambda^2$:
* **Violet ($405\text{ nm}$)**: $P \approx 1.53\text{ cm}$ (tight, dense coils).
* **Green ($532\text{ nm}$)**: $P \approx 2.64\text{ cm}$ (intermediate coil).
* **Red ($670\text{ nm}$)**: $P \approx 4.20\text{ cm}$ (elongated, loose coil).

Because each wavelength possesses a distinct spatial period, the different spectral colors gradually drift out of phase along the tube, decomposing incident white light into spatially separated rainbow bands.

---

### 6. Polychromatic Superposition & Color Perception

Real white light contains a continuum of wavelengths from $380\text{ nm}$ to $750\text{ nm}$. The perceived color at any coordinate $(x, z)$ along the tube is the radiometric integral over the visible spectrum weighted by the human eye's CIE tristimulus color-matching functions $\vec{w}_{\text{sRGB}}(\lambda)$:

$$\vec{C}(z) = \int_{380\text{ nm}}^{750\text{ nm}} S(\lambda) \cdot \cos^2\left(\theta_0 + \frac{A \cdot c \cdot z}{\lambda^2} - \phi_{\text{view}}\right) \cdot L(x) \cdot \vec{w}_{\text{sRGB}}(\lambda) \, d\lambda$$

where:
* $S(\lambda)$ is the spectral power distribution of the source.
* $L(x) = 2\sqrt{R^2 - x^2}$ is the geometric chord length through a cylinder of radius $R$ at lateral offset $x$.
* $\vec{w}_{\text{sRGB}}(\lambda)$ converts monochromatic spectral radiance into sRGB color coordinates.

> [!NOTE]
> In broadband illumination, multiple wavelengths scatter simultaneously from every volume element. The resulting colors are **not** pure monochromatic laser lines, but rather **iridescent, desaturated pastel hues** formed by subtractive extinction, perfectly matching authentic sugar-water polarimetry experiments and 3Blue1Brown's demonstrations.

---

### 7. Dynamical "Walking Stripes" Illusion

When the entrance polarizer angle $\theta_0$ is rotated at constant angular velocity $\omega = \frac{d\theta_0}{dt}$, the total phase becomes time-dependent:

$$\theta(z, \lambda, t) = \omega t + \frac{A \cdot c}{\lambda^2} z$$

Setting the phase to a constant ($\theta = \text{const}$) and taking the total time derivative yields the apparent axial velocity of the scattering stripes:

$$\frac{d\theta}{dt} = \omega + \frac{A \cdot c}{\lambda^2} \frac{dz}{dt} = 0 \implies v_{\text{phase}}(\lambda) = \frac{dz}{dt} = -\frac{\omega \lambda^2}{A \cdot c}$$

Even though the liquid is completely stationary and light travels axially at $c/n \approx 2 \times 10^8\text{ m/s}$, the bright and dark stripes appear to **glide smoothly along the cylinder**. This apparent axial motion functions like an Archimedean screw or a turning barber pole.

---

## 📁 Project Architecture & Layout

```
optics_project/
├── main.py                     # Unified CLI entrypoint (diagnostics, comparison, ord, etc.)
├── plot_ord_relations.py       # Standalone publication-grade ORD & Biot relation graph generator
├── manim_scenes.py             # 5 production Manim CE 3D and 2D animation scenes
├── requirements.txt            # Python dependencies (numpy, matplotlib, plotly, manim)
├── barber_pole/                # Core numerical & optical physics simulation package
│   ├── __init__.py             # Package exports
│   ├── config.py               # Physical constants, default Cauchy A, tube geometry, palette
│   ├── spectral.py             # Cauchy dispersion formula, sRGB conversion, pitch calculator
│   ├── raymarch.py             # Volumetric cylindrical raymarching & optical path integrator
│   ├── diagnostics.py          # 4-panel analytical physics diagnostics figure
│   ├── comparison.py           # Side-by-side comparison (discrete laser trio vs continuous spectrum)
│   ├── dashboard.py            # Interactive Matplotlib GUI with live parameter sliders
│   ├── helix3d.py              # Interactive WebGL 3D polarization helices via Plotly
│   └── animation.py            # Walking stripes GIF / MP4 numerical renderer
├── out/                        # Rendered publication figures, web visualizers, and diagrams
│   ├── ord_dispersion_comprehensive.png  # 6-panel ORD master dashboard
│   ├── ord_curve_theta_vs_lambda.png    # Focused theta(lambda) and Biot linearity curves
│   ├── comparison.png                   # Discrete vs continuous raymarched cylinder comparison
│   ├── diagnostics.png                  # 4-panel physics validation dashboard
│   ├── helix3d.html                     # Standalone interactive 3D WebGL model
│   └── walking_stripes.gif              # Raymarched walking stripes animation
└── media/videos/manim_scenes/  # Rendered Manim video outputs (1080p60)
    └── 1080p60/
        ├── ORDContinuousSpectrum.mp4    # 3D continuous pastel spectrum cylinder ribbon
        └── ...
```

---

## 🚀 Installation & Requirements

Ensure you have Python 3.10+ installed with `ffmpeg` available on your system path.

```bash
# Clone the repository
git clone <repo-url>
cd optics_project

# Install core dependencies
pip install -r requirements.txt
```

### Dependencies
* **Core Physics & Plotting**: `numpy`, `matplotlib`, `scipy`
* **Interactive 3D Web**: `plotly`
* **Mathematical Animation**: `manim` (Manim Community Edition)
* **Video Encoding**: `ffmpeg` (system package)

*(Note: A local LaTeX installation is **not** required to render the Manim scenes; all typographic labels use native Cairo vector text rendering).*

---

## 💻 Running the Simulation & Generating Figures

All simulations and figure generators can be executed through the unified [`main.py`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/main.py) command-line interface or as standalone scripts.

### 1. Optical Rotatory Dispersion (ORD) Helper Graphs
Generates high-resolution publication-quality figures demonstrating the mathematical relationship between rotation angle, wavelength, spatial pitch, and Malus analyzer spectra:

```bash
# Generate comprehensive dashboard and focused curves in out/
python main.py ord --save-dir out

# Or invoke plot_ord_relations.py directly with custom concentration & path length:
python plot_ord_relations.py -c 0.45 -z 15.0 --save-dir out --no-show
```

Outputs generated:
* [`out/ord_dispersion_comprehensive.png`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/ord_dispersion_comprehensive.png): 6-panel comprehensive master dashboard.
* [`out/ord_curve_theta_vs_lambda.png`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/ord_curve_theta_vs_lambda.png): Focused 2-panel curve ($\theta(\lambda)$ with continuous spectrum fill + Biot $1/\lambda^2$ linearity fit).

### 2. Analytical Diagnostics Dashboard
Plots four fundamental optical verification panels: (1) Cauchy rotation $\theta(\lambda)$ for laser lines, (2) spatial helical pitch $P(\lambda)$, (3) sideways scattering intensity profiles $I(z)$, and (4) cylindrical chord-length attenuation $L(x)$:

```bash
python main.py diagnostics --save-dir out
```

### 3. Discrete RGB vs. Continuous Spectrum Comparison
Renders the side-by-side raymarched physical appearance of the tube under discrete 3-laser illumination (Red 650 nm, Green 532 nm, Blue 450 nm) versus broadband continuous white-light illumination (415–675 nm):

```bash
python main.py comparison --save-dir out -c 0.85 --theta0 0.0
```

### 4. Interactive Simulation Dashboard (GUI)
Launches a standalone interactive window with real-time sliders for concentration ($c$), entrance polarizer angle ($\theta_0$), analyzer angle ($\theta_2$), and spectrum mode:

```bash
python main.py dashboard
```

### 5. Interactive 3D WebGL Helices (Plotly)
Generates an interactive 3D HTML model showing the helical trajectory of electric field polarization vectors winding through the cylindrical tube:

```bash
python main.py helix3d --save-dir out
# Opens out/helix3d.html in your default web browser
```

### 6. Raymarched Walking Stripes Animation
Renders an animated GIF/MP4 displaying the continuous translation of scattering stripes as the entrance polarizer rotates:

```bash
python main.py animate --save-dir out -c 0.85
```

### 7. Headless Batch Execution
Run all numerical simulations and figure generations in headless mode (ideal for CI/CD or remote servers):

```bash
python main.py all --save-dir out --no-show
```

---

## 🎬 Manim 3D Mathematical Animations Suite

The repository includes five production-ready Manim scenes in [`manim_scenes.py`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/manim_scenes.py):

```bash
# Preview at low quality (480p15)
manim -pql manim_scenes.py <SceneName>

# Render high quality (1080p60)
manim -pqh manim_scenes.py <SceneName>

# Render 4K production quality (2160p60)
manim -pqk manim_scenes.py <SceneName>
```

| Scene Name | Dimension | Description |
|---|---|---|
| [`LightThroughGlucoseTube`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/manim_scenes.py#L57) | 3D (Vertical) | Shows planar electric field vectors climbing a vertical glucose cylinder. Color-coded Red, Green, and Blue polarization vectors trace distinct helical tracks. The entrance polarizer is then swept through $360^\circ$ to demonstrate rigid axial translation. |
| [`WalkingStripes`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/manim_scenes.py#L200) | 2D (Side-by-Side) | Combines the raymarched volumetric barber pole tube on the left with dynamic $I(z, \lambda) = \cos^2(\theta)$ intensity graphs on the right, dynamically illustrating phase velocity during rotation. |
| [`DispersionDial`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/manim_scenes.py#L283) | 2D Dial | A real-space polarization clock. A probe scans along the tube axis $z$, showing how collinear polarization vectors fan out chromatically across the dial; then $\theta_0$ is rotated to show rigid dial rotation. |
| [`ORDLightSplitting`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/manim_scenes.py#L371) | 3D (Horizontal) | Oriented along the horizontal $x$-axis. Linearly polarized white light enters at $x = 0$ and splits into 5 discrete laser helices (Red, Yellow, Green, Cyan, Blue), followed by dynamic camera orbiting and polarizer rotation. |
| [`ORDContinuousSpectrum`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/manim_scenes.py#L637) | 3D (Horizontal) | **Flagship 3D scene**: Visualizes incident white light splitting into a continuous, desaturated pastel rainbow helical ribbon twisting through the transparent glass cylinder. Includes a continuous spectrum color bar, floating fanning dial wavefront, and entrance polarizer sweep. |

---

## 📊 Summary of Generated Output Artifacts

| File | Type | Description |
|---|---|---|
| [`out/ord_dispersion_comprehensive.png`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/ord_dispersion_comprehensive.png) | PNG (3840×2400) | 6-panel physics master dashboard: $\theta(\lambda)$ curve, Biot linearity, helical pitch $P(\lambda)$, polarization dial, Malus transmission, and dispersion spread $\Delta\theta(z)$. |
| [`out/ord_curve_theta_vs_lambda.png`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/ord_curve_theta_vs_lambda.png) | PNG (3200×1400) | Focused 2-panel figure: Cauchy rotation with smooth sRGB underfill and Biot $1/\lambda^2$ linear fit. |
| [`out/comparison.png`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/comparison.png) | PNG (1600×1200) | Numerical raymarched comparison between discrete 3-laser illumination and continuous spectrum. |
| [`out/diagnostics.png`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/diagnostics.png) | PNG (1600×1200) | 4-panel analytical validation of Cauchy rates, spatial pitch, scattering curves, and chord lengths. |
| [`out/helix3d.html`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/helix3d.html) | HTML / WebGL | Standalone interactive 3D WebGL model of the polarization helices. |
| [`out/walking_stripes.gif`](file:///home/aneeshbhate/acads/ph3050/project/optics_project/out/walking_stripes.gif) | Animated GIF | Dynamic demonstration of axial stripe translation under continuous entrance polarizer rotation. |
| `media/videos/manim_scenes/1080p60/ORDContinuousSpectrum.mp4` | MP4 (1080p60) | Full 3D continuous spectrum Manim animation (30.5 s, 60 fps). |

---

## 👥 Authors & Attribution

* **Simulation, Theory & Architecture**: Kartik Khare, Aneesh Bhate, Dhairya Nisar, Gouri Mittal
* **Course Context**: *Made for PH3050 / Engineering Optics*
* **Professor**: *Dr. Arif Warsi Laskar*
* **Inspirations**: 
  - 3Blue1Brown's visual exposition on *Polarization & Optical Activity*
  - Biot (1815) & Cauchy (1836) classical dispersion treatises
  - Classical polarimetry and Rayleigh transverse dipole scattering demonstrations
