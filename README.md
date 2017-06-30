pyMOSChar, a MOSFET Characterization package, is a python port of the gm/ID
starter kit by Prof. Boris Murmann of Stanford University. It provides
functions to characterize MOSFETs using simulators (spectre and ngspice are
supported for now) and lookup the data.  This saves you from running DC
simulations every time you begin circuit design and quickly generate plots that
give you an intuitive picture of how the MOSFETs behave in a particular
process. There are three modules available:

1. spice3read: Currently supports reading the SPICE3RAW files generated in DC
simulations by ngspice and spectre. Features to be implemented include support
for eldo and hspice, functions to plot data stored in the rawfile.
2. charMOS: Peforms the characterization of the MOSFET one is interested in. 
Currently works with ngspice and spectre. Support for eldo and hspice will be 
added soon. Currently stores ID, Vt, gm, gmb, gds, cgg, cgs, cgd, cgb, cdd, css
as functions of L, VSB, VDS and VGS (in 4-D arrays).
3. lookupMOS: Provides a lookup function for the characterized data. The 
function performs linear interpolation to extract data points from what is 
stored by charMOS.

The package works only with Python 2.7. I do plan to add support for Python 3
some time in the future. Also contained are usage examples: charMOSExample.py
and lookupExamples.py

For the gm/ID starter kit, written for MATLAB, please refer to the 'Links'
section at Prof. Murmann's website: https://web.stanford.edu/~murmann. I would
like to thank Prof. Murmann for giving permission to use his work and release
this package under the GNU Public License.

### TODO
1. Add the lookupVGS function.
2. Add mode 3 for the lookup function.
3. Add support for Eldo and HSPICE.
4. Packaging and documentation.
