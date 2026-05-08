# %%
from iertools.read import read_sql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# %%
f = "../osm/004_dos_zonas/run/eplusout.sql"
base = read_sql(f, alias=True).data
base.head()

# %%
# Inspeccionar columnas disponibles
print(base.columns.tolist())

# %%
# --- Temperatura de neutralidad mensual ---
# Tn = 13.5 + 0.54 * To_m,  con To_m = promedio mensual de la T exterior
To_m = base['To'].groupby(base.index.month).mean()
Tn_m = 13.5 + 0.54 * To_m

resumen_mensual = pd.DataFrame({'To_m': To_m, 'Tn': Tn_m})
resumen_mensual.index.name = 'mes'
resumen_mensual

# %%
# Mapear la Tn de cada mes a cada paso de 10 min de la serie
Tn_serie = pd.Series(base.index.month.map(Tn_m).values, index=base.index)

# Banda de confort recomendada por la norma adaptativa: Tn ± 2.5 °C
banda = 2.5 # tomar con cuidado
T_sup = Tn_serie + banda
T_inf = Tn_serie - banda

# %%
# --- Grados-hora de disconfort para una zona (Ti_ESTE) ---
Ti = base['Ti_ESTE']

# Paso temporal: 10 minutos = 1/6 h
dt_h = 10 / 60

exc_calor = (Ti - T_sup).clip(lower=0)
exc_frio  = (T_inf - Ti).clip(lower=0)

GH_calido = (exc_calor * dt_h).sum()
GH_frio   = (exc_frio  * dt_h).sum()

print(f"GH disconfort cálido (Ti_ESTE): {GH_calido:9.1f} °C·h")
print(f"GH disconfort frío   (Ti_ESTE): {GH_frio:9.1f} °C·h")

# %%
# Desglose mensual de los GH
gh_mensual = pd.DataFrame({
    'GH_calido': (exc_calor * dt_h).groupby(exc_calor.index.month).sum(),
    'GH_frio':   (exc_frio  * dt_h).groupby(exc_frio.index.month).sum(),
})
gh_mensual.index.name = 'mes'
gh_mensual

# %%
# --- Visualización: separación confort / cálido / frío ---
confort = (Ti >= T_inf) & (Ti <= T_sup)
calor   = Ti > T_sup
frio    = Ti < T_inf

fig, ax = plt.subplots(figsize=(14, 5))
ax.scatter(Ti.index[confort], Ti[confort], s=2, color='tab:green', label='Confort')
ax.scatter(Ti.index[calor],   Ti[calor],   s=2, color='tab:red',   label='Disconfort cálido')
ax.scatter(Ti.index[frio],    Ti[frio],    s=2, color='tab:blue',  label='Disconfort frío')

ax.plot(base.index, Tn_serie, color='black', lw=1.0, label='Tn (mensual)')
ax.plot(base.index, T_sup,    color='gray',  lw=0.8, ls='--', label=f'Tn ± {banda} °C')
ax.plot(base.index, T_inf,    color='gray',  lw=0.8, ls='--')

ax.set_xlabel('Fecha')
ax.set_ylabel('Temperatura interior (°C)')
ax.set_title(
    f'Ti_ESTE vs banda de confort adaptativo  '
    f'(GH cálido = {GH_calido:.0f} °C·h, GH frío = {GH_frio:.0f} °C·h)'
)
ax.legend(loc='upper right', markerscale=4)
plt.tight_layout()
plt.show()

# %%
# --- Temperatura pesada por volumen ---
# Promedio de las Ti_* del dataframe ponderado por el volumen de cada zona
cols_Ti = [c for c in base.columns if c.startswith('Ti_')]
print('Columnas Ti encontradas:', cols_Ti)

# Volúmenes asumidos por zona (m³) — distintos a propósito
volumenes = {
    'Ti_ESTE':  75.0,
    'Ti_OESTE': 45.0,
}

V_total = sum(volumenes[c] for c in cols_Ti)
T_pesada = sum(base[c] * volumenes[c] for c in cols_Ti) / V_total
T_pesada.name = 'Ti_pesada'

print(f'Volumen total: {V_total} m³')
T_pesada.head()

# %%
# Comparación rápida: cada Ti_ vs la T pesada (primer mes)
ini, fin = '2006-01-01', '2006-01-31'
fig, ax = plt.subplots(figsize=(14, 4))
for c in cols_Ti:
    ax.plot(base.loc[ini:fin].index, base.loc[ini:fin, c],
            lw=0.8, alpha=0.7, label=f'{c} (V={volumenes[c]} m³)')
ax.plot(T_pesada.loc[ini:fin].index, T_pesada.loc[ini:fin],
        color='black', lw=1.2, label='Ti pesada')
ax.set_xlabel('Fecha')
ax.set_ylabel('Temperatura (°C)')
ax.set_title('Temperaturas zonales y T pesada por volumen — enero')
ax.legend()
plt.tight_layout()
plt.show()

# %%
