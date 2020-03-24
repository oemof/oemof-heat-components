"""
example, which shows the difference between the new approach and a fix
efficiency
"""

from oemof.thermal.concentrating_solar_power import csp_precalc
import pandas as pd
import matplotlib.pyplot as plt

# precaluculation #

dataframe = pd.read_csv('csp_data/data_Muscat_22_8.csv')
dataframe['Datum'] = pd.to_datetime(dataframe['Datum'])
df_temp_amb_series = pd.read_csv('csp_data/data_Muscat_22_8_midday.csv')
temp_amb_series = pd.read_csv('csp_data/temp_ambience.csv')['t_amb']

# parameters for the precalculation
periods = 24
latitude = 23.614328
longitude = 58.545284
timezone = 'Asia/Muscat'
collector_tilt = 10
collector_azimuth = 180
cleanliness = 0.9
a_1 = -8.65e-4
a_2 = 8.87e-4
a_3 = -5.425e-5
a_4 = 1.665e-6
a_5 = -2.309e-8
a_6 = 1.197e-10

eta_0 = 0.78
c_1 = 64
c_2 = 0
temp_collector_inlet = 435
temp_collector_outlet = 500

# plot showing the difference between a constant efficiency without considering
# cleaniness for the heat of the collector during a day
data_precalc = csp_precalc('22/08/2003', periods, 'H',
                           latitude, longitude, timezone,
                           collector_tilt, collector_azimuth, cleanliness,
                           eta_0, c_1, c_2,
                           temp_collector_inlet, temp_collector_outlet,
                           a_1, a_2, a_3, a_4, a_5, a_6,
                           E_dir_hor=dataframe['E_dir_hor'],
                           loss_method='Andasol',
                           date_col='Datum', temp_amb_input=dataframe['t_amb'])

heat_calc = data_precalc['collector_heat']
irradiance_on_collector = (data_precalc['collector_irradiance']
                           / (cleanliness**1.5))
heat_compare = irradiance_on_collector * eta_0
t = list(range(1, 25))


fig, ax = plt.subplots()
ax.plot(t, heat_calc, label='CSP precalculation')
ax.plot(t, heat_compare, label='constant efficiency')
ax.set(xlabel='time (h)', ylabel='Q_coll',
       title='Heat of the collector')
ax.grid()
ax.legend()
plt.savefig('compare_precalculations.png')

# plot showing the difference between a constant efficiency and the efficiency
# depending on the ambient temperature for the same irradiance and hour of the
# day
df_result = pd.DataFrame()
for i in range(len(temp_amb_series)):
    df_temp_amb_series['t_amb'] = temp_amb_series[i]
    data_precalc_temp_amb = csp_precalc(
        '2003-01-01 12:00:00', 1, 'H',
        latitude, longitude, timezone,
        collector_tilt, collector_azimuth, cleanliness,
        eta_0, c_1, c_2,
        temp_collector_inlet, temp_collector_outlet,
        a_1, a_2, a_3, a_4, a_5, a_6,
        loss_method='Andasol',
        E_dir_hor=df_temp_amb_series['E_dir_hor'],
        date_col='Datum', temp_amb_input=df_temp_amb_series['t_amb'])

    df_result = df_result.append(data_precalc_temp_amb, ignore_index=True)

fig, ax = plt.subplots()
ax.plot(temp_amb_series, df_result['eta_c'],
        label='efficiency depending on ambient temperature')
ax.plot(temp_amb_series, [eta_0] * 24, label='constant efficiency')
ax.set_ylim(0, 1)
ax.set(xlabel='ambient temperature', ylabel='eta_collector',
       title='collectors efficiency')
ax.grid()
ax.legend()
plt.show()
plt.savefig('compare_temp_dependency.png')
