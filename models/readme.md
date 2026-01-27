This folder contains the raw model data.

Each file name is as such:

<code>prof.\<line>.\<geometry>.\<Mdot>.\<Tmax>.\<Inclination>.0</code>

- line: which line is modeled (Hα = h23, Hβ = h24, CaII = Ca)
- geometry: the geometry of the disk, this is of the form GXX, where X is between 01-36. 
- Mdot: the accretion rate, this is of the form MXX, where X is between 01-36
- Tmax: the maxmimum temperature, this is of the form TXX, where X is between 01-36
- Inclination: the inclination of the disk in degrees, this is of the form IXX, where X is any of [15, 30, 45, 60, 75].

The file XXXXX.csv lists the correspondences between an ID number
and the model parameters. 

An example file name is <code>prof.h23.G01.M01.T03.I45.0</code>, 
which would query the Hα line with a geometry of R<sub>in</sub>=2, R<sub>out</sub>=0.5, an accretion rate of -7, max temperature of 9500K, and an inclination of 45 degrees.

