Pyngspice provides functions to characterize MOSFETs using simulators and lookup
the data. There are three modules available:

1. pltNgspice: Currently supports reading the SPICE3RAW file outputs generated 
by ngspice and spectre. Features to be implemented include support for eldo and 
hspice, functions to plot data stored in the rawfile.
2. charMOS: Peforms the characterization of the MOSFET one is interested in. 
Currently works with ngspice and spectre. Support for eldo and hspice will be 
added soon. Currently stores ID, Vt, gm, gmb, gds, cgg, cgs, cgd, cgb, cdd, css
as functions of L, CSB, VDS and VGS (in 4-D arrays).
3. lookupMOS: Provides a lookup function for the characterized data. The 
function performs linear interpolation to extract data points from what is 
stored by charMOS.

Also contained are usage examples: charMOSExample.py, charMOSExampleSpectre.py 
and lookupExamples.py