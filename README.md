# ITCZ-diagnostic

This tool allows you to identify sources of rainfall differences in simulations, which is based on a conceptual framework by [Emanuel, 2019](https://doi.org/10.1175/JAS-D-18-0090.1).<br>
A detailed description of the tool can be found in [Jung et al., 2023](https://doi.org/10.5194/wcd-2023-7), which is currently under review.

Using this tool, you can calculate convective updraft mass flux $M_u$ and precipitation efficiency $\epsilon_p$ in a physically consistent way through the equations:

$$\eqalign{M_u &= \frac{1}{1-\epsilon_p} \Big( \frac{F_\mathrm{h} }{h_\mathrm{b}-h_\mathrm{m}} - \frac{\dot Q}{S}\Big), \\
\\
\mathrm{Pr} &= \epsilon_p  M_u \langle q_v \rangle.}$$

Input variables:
|         Symbols       |                Variable name                |
| :-------------------: | ------------------------------------------- |
| $F_\mathrm{h}$        | Surface enthalpy fluxes                     |
| $h_\mathrm{b}$        | Moist static energy in the boundary layer   |
| $h_\mathrm{m}$        | Moist static energy in the free troposphere |
| $\dot Q$              | Radiative cooling rate                      |
| $S$                   | Dry static stability                        |
| $\mathrm{Pr}$         | Precipitation rate                          |
| $\langle q_v \rangle$ | Column averaged specific humidity           |

Output variables:
|         Symbols       |                Variable name                |
| :-------------------: | ------------------------------------------- |
| $M_u$                 | Convective updraft mass flux                |
| $\epsilon_p$          | Precipitation efficiency                    |

The core script is `itcz-tools/KE_framework_full.py`, but all input variables have to be specified. Currently, the code is not flexible.
