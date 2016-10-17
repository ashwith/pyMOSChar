import pickle 
import numpy as np
from scipy.interpolate import interpn

mosDat = None

def init(fileName='MOS.dat'):
    global mosDat
    
    print "Loading MOSFET data. Please wait..."
    mosDat = pickle.load(open(fileName, 'rb'))
    print "Loading complete!"

def reset():
    global mosDat
    mosDat = None

def lookup(mosType, *outVars, **inVars):

    # Check if a valid MOSFET type is specified.
    mosType = mosType.lower()
    if (mosType not in ['nfet', 'pfet']):
        print("ERROR: Invalid MOSFET type. Valid types are 'nfet' and 'pfet'.")

    defaultL = min(mosDat[mosType]['length'])
    defaultVGS = mosDat[mosType]['vgs']
    defaultVDS = max(mosDat[mosType]['vds'])/2;
    defaultVSB  = 0;

    # Figure out the mode of operation and the requested output arguments.
    # Mode 1 : Just one variable requested as output.
    # Mode 2 : A ratio or product of variables requested as output.
    # Mode 3 : Two ratios or products of variables requested as output.
    mode = 1
    outVarList = []

    if (len(outVars) == 2):
        mode = 3
        for outVar in outVars:
            if (type(outVar) == str):
                if (outVar.find('/') != -1):
                    pos = outVar.find('/')
                    outVarList.append(outVar[:pos].lower())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].lower())
                elif (outVar.find('*') != -1):
                    pos = outVar.find('*')
                    outVarList.append(outVar[:pos].lower())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].lower())
                else:
                    print "ERROR: Outputs requested must be a ratio or product of variables"
                    return None
            else:
                print "ERROR: Output variables must be strings!"
                return None
    elif (len(outVars) == 1):
        outVar = outVars[0]
        if (type(outVar) == str):
            if (outVar.find('/') == -1 and outVar.find('*') == -1):
                mode = 1
                outVarList.append( outVar.lower())
            else:
                mode = 2
                if (outVar.find('/') != -1):
                    pos = outVar.find('/')
                    outVarList.append(outVar[:pos].lower())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].lower())
                elif (outVar.find('*') != -1):
                    pos = outVar.find('*')
                    outVarList.append(outVar[:pos].lower())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].lower())
        else:
            print "ERROR: Output variables must be strings!"
            return None
    else:
        print "ERROR: No output variables specified"
        return None
    
    # Figure out the input arguments. Set to default those not specified.
    varNames = [key for key in inVars.keys()]

    for varName in varNames:
        if (not varName.islower()):
            print "ERROR: Keyword args must be lower case. Allowed arguments: l, vgs, cds and vsb."
            return None
        if (varName not in ['l', 'vgs', 'vds', 'vsb']):
            print "ERROR: Invalid keyword arg(s). Allowed arguments: l, vgs, cds and vsb."
            return None

    L = defaultL
    VGS = defaultVGS
    VDS = defaultVDS
    VSB = defaultVSB
    if ('l' in varNames):
        L = inVars['l']
    if ('vgs' in varNames):
        VGS = inVars['vgs']
    if ('vds' in varNames):
        VDS = inVars['vds']
    if ('vsb' in varNames):
        VSB = inVars['vsb']
    
    xdata = None
    ydata = None
    
    # Extract the data that was requested
    if (mode == 1):
        ydata = mosDat[mosType][outVarList[0]]
    elif (mode == 2 or mode == 3):
        ydata = eval("mosDat[mosType][outVarList[0]]" + outVarList[1] + "mosDat[mosType][outVarList[2]]")
        if (mode == 3):
            xdata = eval("mosDat[mosType][outVarList[3]]" + outVarList[4] + "mosDat[mosType][outVarList[5]]")
            
    
    # Interpolate for the input variables provided
    if (mosType == 'nfet'):
        points = (mosDat[mosType]['length'], -mosDat[mosType]['vsb'], mosDat[mosType]['vds'], mosDat[mosType]['vgs'])
    else:
        points = (mosDat[mosType]['length'],  mosDat[mosType]['vsb'], -mosDat[mosType]['vds'], -mosDat[mosType]['vgs'])
    
    xi_mesh = np.array(np.meshgrid(L, VSB, VDS, VGS))
    xi = np.rollaxis(xi_mesh, 0, 5)
    xi = xi.reshape(xi_mesh.size/4, 4)

    len_L = len(L) if type(L) == np.ndarray or type(L) == list else 1
    len_VGS = len(VGS) if type(VGS) == np.ndarray or type(VGS) == list else 1
    len_VDS = len(VDS) if type(VDS) == np.ndarray or type(VDS) == list else 1
    len_VSB = len(VSB) if type(VSB) == np.ndarray or type(VSB) == list else 1

    if (mode == 1 or mode == 2):
        result = np.squeeze(interpn(points, ydata, xi).reshape(len_L, len_VSB, len_VDS, len_VGS))
    elif (mode == 3):
        print "ERROR: Mode 3 not supported yet :-("

    # Return the result
    return result
