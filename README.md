# krp_python_telemetry

Telemetry for [Kart Racing Pro](https://www.kartracing-pro.com/) using Python notebook ([Jupyter](https://jupyter.org/))


## Notebbok
### Screenshots

Plot various data such as Engine (rpm), Distance,	CylHeadTemp	(°C), WaterTemp (°C), Gear, Speed	(km/h), LatAcc (G), LonAcc (G), Steer (°), Throttle (%), Brake (%), FrontBrakes (%), Clutch (%), YawVel (deg/s)

- engine (rpm) vs laptime
![Engine_vs_Laptime](screenshots/Engine_vs_Laptime.PNG)

- engine (rpm) vs Distance

![Engine_vs_Distance](screenshots/Engine_vs_Distance.PNG)

Compare trajectory among differents laps

![Engine_vs_Distance](screenshots/Trajectory.PNG)


### Installation

Install a scientific distribution of Python such as [Anaconda Python](https://www.anaconda.com/download) 

Dependencies:
- [Numpy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/)

Run notebook using

    $ jupyter notebook

## Application

Dependencies:
- same as previously mentioned +
- [Taipy](https://www.taipy.io/)

Run application locally using:

    $ poetry run taipy run krp_python_telemetry/telemetry.py

Deployed on [Taipy Cloud](https://www.taipy.io/cloud/)

    Browse to https://krp-telemetry.taipy.cloud/


## See also
- KaRTA
  - http://www.lautrup.se/KaRTA/
  - https://github.com/flautrup/KaRTA

