#!/usr/bin/python

import numpy
import string
import random #randomised initial positions. Goal: make deterministic option
import subprocess as sb #for opening files and communicating with OS
from Gconst import au
from math import pi

from OrbitDefaults import *
import optparse # command line options

purepythondefault = False


##########################################
## 
## Command line options and default values
##
##########################################

parser = optparse.OptionParser()

parser.add_option("-p", "--pure-python", dest="purepython",
                  default=purepythondefault,
                  help="Choose whether to use only pure python variants of submodules (default: False)")
parser.add_option("-a", "--asteroid-number",
                  dest="asteroidnumber",
                  default=asteroidnumber,
                  help="Select integer number of asteroids (main belt PlanetClass objects with"+
                  " random masses between 1e8 and 1e18 and random semimajor axes between 1.5 mars"+
                  " orbits and 0.8 jupiter orbits) to be included (default: %d)" % asteroidnumber)
parser.add_option("-g", "--granularity",
                  dest="granularity",
                  default=granularity,
                  help="Select time betweeen successive calculation (coarseness of similation), in seconds; "+
                  "up to a day (86400) or so should be sufficient for most planets except during close "+
                  "encounters, smaller for moons. Default: %d "% granularity)
parser.add_option("-I", "--iterations", dest="numberofiterations",
                  default=numberofiterations, help="Select integer number of iterations (together "+
                  "with granularity, this gives the timeframe simulated). Default: %d"% numberofiterations)
parser.add_option("-r", "--realplanets",dest="userealplanets",
                  default=userealplanets,
                  help="Use real planets from NASA Planet Factsheet, "+
                  "default True; 0 or `False': randomly generate planets (might be buggy)")
parser.add_option("-n", "--planetnumber", dest="randomplanetnumber", default=randomplanetnumber,
                  help="number of planets (only has an effect with random planets")
parser.add_option("-R", "--numberofruns", dest="numberofruns", default=numberofruns,
                  help="Number of simulations to be run with these parameters; default: %d" % numberofruns)
parser.add_option("-V", "--include-vagrant", dest="vagrant_included", default=str(vagrant_included),
                  help="Choose to throw a passing brown dwarf (0.01 sun masses) at the inner solar system (default %d)" % vagrant_included)

parser.add_option("-b", "--blur", dest="blur",default=blur,
                  help="Select random factor (between 0 and 1) by which the actual interval between iterations is varied to reduce resonance artifacts (default=%0.2f" % blur)
parser.add_option("-d", "--display-standards", dest="displaystandards", default=displaystandards, help="Display a standard set of graphical representation upon completion")
parser.add_option("-i", "--interactivemode", dest="interactivemode", default=interactivemode, help="Allow command line interaction to change individual planets' properties (requires a good understanding of the program!)")
(options, args) = parser.parse_args()


#start = time.time()

asteroidnumber = int(options.asteroidnumber)
granularity = float(options.granularity)
numberofiterations = int(options.numberofiterations)
userealplanets = bool(eval(options.userealplanets))
randomplanetnumber = int(options.randomplanetnumber)
numberofruns = int(options.numberofruns)
vagrant_included = bool(eval(options.vagrant_included))
blur = float(options.blur)
displaystandards = bool(eval(options.displaystandards))
interactivemode = bool(eval(options.interactivemode))


if options.purepython:
    purepython = eval(options.purepython)
    
else:
    purepython = purepythondefault
# costum submodules:
if purepython:
    from oldplanetclass import *
    from oldplanetsystem import *
    from oldorbitdisplaytools import *
else:    
    from PlanetClass import *
    from PlanetSystem import *
    from OrbitDisplayTools import *




print options
    
planetlistfile = open("planetlistNASA.txt", "r")

planetlist = [[planobject.strip().strip("*") for planobject in parameter.split("\t")] for parameter in planetlistfile.read().split("\n") if parameter]
planetlistfile.close() #the file includes Moon with a * to note that its orbit parameters are given relative to earth


def getcmdinput():
                inputstring = raw_input("Please enter manual changes!\n> ")
                #exec(inputstring)
                if inputstring == "pass":
                    return 0
                elif inputstring == "1":
                    print "Select object to modify properties"
                    modifydict = {}
                    for idx, plan in enumerate(solar_system):
                        print idx, plan.name
                        modifydict[str(idx)] = plan
                    selected_planet = modifydict[raw_input("Select planet by number> ")]
                    print "now select property to adjust!"
                    propertylist = [("position", "absolute position"), ("mass", "mass"), ("velocity", "velocity vector"), ("distance", "distance_from_parent")]
                    propertydict = {idx:prop for idx,prop in enumerate(propertylist)}
                    print propertydict
                    for idx, entry in enumerate(propertylist):
                        print idx, propertydict[idx][1],
                        print propertydict[idx][0]
                        #print "current setting", (selected_planet).(eval(propertydict[idx][0]))
                    

#print planetlist
sun=planet("Sun", 1.989e30, [0,0,0],[0,0,0], "y")

parsedplanetlist = []
for index in range(len(planetlist[0])):
    planetname = planetlist[0][index]
    if planetname:
        dictname = planetname+"_dict"
        exec(dictname+" = dict()", locals())
        for line in planetlist[1:]:
            eval(dictname, locals())[line[0]] = float(line[index].replace(",",""))
        planetmass = eval(dictname, locals())["Mass (1024kg)"] * 1e24
        planetdistance = eval(dictname, locals())["Distance from Sun (106 km)"] * 1e9
        planetradius = eval(dictname, locals())["Diameter (km)"] * 500
        inclination = eval(dictname)["Orbital Inclination (degrees)"] * 2 * pi / 360.
        if planetname == "MOON":
            central = earth
        else:
            central = sun
        orbitparas = DeriveOrbitParameters(planetdistance, inclination, central.mass,)
        position = orbitparas.position + central.position
        velocity = orbitparas.velocity + central.velocity
        colors = "green red magenta yellow orange pink purple brown cyan".split()
        currentplanet = planet(planetname, planetmass, position, velocity, color=hexstring(random.randrange(16**6)))
        exec(string.lower(planetname)+" = currentplanet", locals())
        parsedplanetlist.append(currentplanet)
        
        
for run in range(numberofruns):
    sun=planet("Sun", 1.989e30, [0,0,0],[0,0,0], "y")
    
    
    #print vagrant_initstring
    savefolder = vagrant_initstring = str(int(time.time()))
    
    solar_system = PSystem([sun], name=savefolder, folderlocation=savefolder)
    sb.call((["mkdir", savefolder]))
    
    for i in xrange(asteroidnumber): #seed the system with n random main belt asteroids
                # masses 10^8 to 9.9999 * 10^19, logarithmically distributed
                # distances uniformly distributed between 1.5 mars orbits and
                #0.8 jupiter orbits
        asteroidname = "asteroid" + zeropad(i, len(str(asteroidnumber-1)))
        solar_system.addplanet(makeasteroid(asteroidname,sun, astdistancerange=(distance(mars.position, sun.position)*1.5, distance(jupiter.position, sun.position)*0.8)))
    print [pobject.name for pobject in solar_system]
    print "most massive object", [pobject.name for pobject in solar_system if pobject.mass == max([mmass for mmass in [plobject.mass for plobject in solar_system]])]
    
    
    
    for parsedplanet in parsedplanetlist:
        parsedplanet.setparent(sun)
        if useallplanets == 1 and userealplanets:
            solar_system.addplanet(parsedplanet)
    if userealplanets==False:
        for i in range(randomplanetnumber):
            planetname = "planet" + str(i)
            randomplanet = RandomPlanet(name=planetname, parent=sun, distancerange=(0.2 * au, 40 * au), inclinationrange=0.05).planet
            solar_system.addplanet(randomplanet)
        
    #if earth in solar_system:
        #moonorbit = DeriveOrbitParameters(earth)
        #moon = planet("Moon",0.073e24, earth.position + [0, 0.384e9, 0], earth.velocity + [1010,0,0], "grey")

        #solar_system.addplanet(moon)

    
    if vagrant_included:
        vagrantinitialvelocity = 26000
        vagrantinitialdistance = distance(earth.position, sun.position)*100
        vagrant_initialvelocity = [random.gauss(0,200), -12000 + random.gauss(0,200), -24000]
        vagrant_star = planet("Oumuamua", 6e10, earth.position + [0,vagrantinitialdistance/2.0, vagrantinitialdistance] , vagrant_initialvelocity, "k")
        vs_position_rel, vs_velocity_rel = DeriveOrbitParameters(15*au, 0.2, vagrant_star.mass).get_parameters()
        #vagrant_secondary = planet("VagrantB", sun.mass/40, vs_position_rel+vagrant_star.position, -vs_velocity_rel+vagrant_star.velocity, "grey")
        #vagrant_star.velocity -= vs_velocity_rel * vagrant_secondary.mass / vagrant_star.mass
        #vsystem_mass = vagrant_star.mass * vagrant_secondary.mass
        #vagrant_star.position -= vs_position_rel * vagrant_secondary.mass / (vagrant_secondary.mass / vsystem_mass)
        vagrant_sattelites = 0
        solar_system.addplanet(vagrant_star)
        #solar_system.addplanet(vagrant_secondary)
        if vagrant_sattelites:
            vagrantsattelitelist = list()
            for sattelite in range(vagrant_sattelites):
                sattelitename = "sattelite"+zeropad(sattelite,len(str(vagrant_sattelites)))
                parsedsattelite = RandomPlanet(sattelitename, vagrant_star, (0.1 * au ,2 * au ), massrange=(1e21,3e26)).planet
                solar_system.addplanet(parsedsattelite)
                vagrantsattelitelist.append(parsedsattelite)
    if interactivemode:
        
                
        
        getcmdinput()
    
    solar_system.savestatus()
    sb.call(("open %s" % savefolder+"/"+solar_system.outfilename), shell=True)

    solar_system.makevelocitydataagearray(granularity)
    solar_system.updatearray(granularity, initialising=1)
    numberofchecks = int(numberofiterations/noisiness+1)
    totaliterations = 0
    for block in range (numberofchecks):
        current_block_iterations = min([block*noisiness+noisiness, numberofiterations])-block*noisiness
        
        #print current_block_iterations
        totaliterations += current_block_iterations
        for i in xrange(block*noisiness, min([block*noisiness+noisiness, numberofiterations])):
            solar_system.updatearray(granularity * random.uniform(1-blur, 1+blur))
 
        #print totaliterations
        #exit()
        #print dir()
        try:
            print distance(sun.position, vagrant_star.position)
        except NameError: pass
        #def saxgen(String):
        #    if String[-1].lower() in "sx":
        #        return String+"'"
        #    else:
        #        return String + "'s"
        #for pplanet in solar_system:
        #    print gravityacceleration(earth, pplanet),
        #    print saxgen(pplanet.name)+" gravitational effect on earth"
    for given_planet in solar_system:
            planetfilename = savefolder+"/"+solar_system.outfilename[:-4]+given_planet.name+"_positions.txt" # ugly string joining is ugly
            planetfile = file(planetfilename, "a")
            j = 0
            for line in given_planet.positionarchive:
                for entry in line:
                    planetfile.write(str(entry)+"\t")
                planetfile.write(str(j)+"\n")
                j += 1
    if displaystandards == True:
        for pplanet in solar_system:
            pplanet.positionarchive = numpy.array(pplanet.positionarchive)
        try:
            try:
                try:
                    if vagrant_included:
                        display_xcentric(vagrant_star, solar_system, 5 * au, 5 * au, savepath = savefolder, name="trajectories relative to brown dwarf")
                    display_xcentric(earth, [moon], 1e9,1e9, savepath = savefolder, name = "Moon orbit")
                    display_distances(earth, [moon],logscale = False, sampling_rate = granularity)
                    #display_distances(earth, solar_system, logscale=True, sampling_rate = granularity)
                except ValueError: pass
            except IndexError: pass
        except NameError: pass
        display_xcentric(sun, solar_system, savepath = savefolder, name = "Solar system large")
        display_xcentric(sun, solar_system, 2*au, 2*au, savepath = savefolder, name = "Inner solar system")
        display_distances(sun, solar_system,logscale=True, sampling_rate = granularity, name="distances from sun")
        display_distances(vagrant_star, solar_system,logscale=True, sampling_rate = granularity, name= "distances from vagrant star")
        display_xcentric(sun, solar_system, 2*au,2*au/5, savepath = savefolder, name = "Sideview of inner solar system (inclinations * 5)", orientation=(1,2))

        def sty(seconds): # seconds to years
             return seconds / 365.24 / 24 / 3600

        its_per_year = int(1/sty(granularity))

        print its_per_year, "its_per_year"

        startpos = 0

        year = 0
        
        year_in_range = True
        while year_in_range: 
            if year < 20 or year%5 == 0: # output trajectories for each of the first 20 years, and once every 5 years henceforth, individually
                display_xcentric(sun, solar_system, savepath = savefolder, name = "Solar system large, year %s" % str(2017+year), timerange=(startpos, startpos+its_per_year))
                display_xcentric(sun, solar_system, 2*au, 2*au, savepath = savefolder, name = "Inner solar system, year %s" % str(2017+year), timerange=(startpos, startpos+its_per_year))
                display_xcentric(earth, [moon], 1e9,1e9, savepath = savefolder, name = "Moon orbit, year %s" % str(2017+year), timerange=(startpos, startpos+its_per_year))
                display_distances(sun, solar_system,logscale=True, sampling_rate = granularity, name="distances from sun, year "+str(2017+year), timerange=(startpos, startpos+its_per_year))
            year += 1
            startpos += its_per_year
            #print "new starting position", startpos
        
            if startpos >= len(sun.positionarchive):
                year_in_range = False
    
    for pplanet in solar_system:
        pplanet.positionarchive = []

t1velocities = []
class Planetdataholder:
    def __init__(self, name):
     self.name = name
     self.positions = []
     self.velocities = []
     self.record = "data*%s_positions.txt" % self.name
    def readinitposition(self, String):
     stringcleared = String.strip(string.punctuation).split()
     self.initialposition = [eval(i) for i in stringcleared]
     self.positions.append(self.initialposition)
    def readinitvelocity(self, String):
     stringcleared = String.strip(string.punctuation).split()
     self.initialvelocity = [eval(i) for i in stringcleared]
    def readfromrecord(self, lineorstring, initialising = 0):
        global t1velocities
        rawline = open(self.record, "r").readline().split()
        
        self.positions.append([float[i] for i in rawline[:3]])
    
     
#for line in basedata:
#   parsed = [entry for entry in line.split("\t") if entry]
#   exec("thisitem = %s = Planetdataholder('%s')" % (parsed[0], parsed[0]))
#   thisitem.readinitposition(parsed[1])
#   thisitem.readinitvelocity(parsed[2])
