
asteroidnumber = 10 # complexity grows exponentionally with number of objects, so be careful!
verticalnoisetype = 1 # 1: absolute, 0: relative to sun distance
verticalnoise = 100000 # standard deviation of planets' position on z-axis, in absolute terms (metres)
#verticalnoise = 0.04 # standard deviation of planets' position on z-axis in radians, to be used with verticalnoisetype 0
granularity = 60*60*8   # minimal time betweeen successive calculations, in seconds
        # up to a day or so (86400) should be unproblematic except for moons on narrow orbits, worse if those are highly eccentric
numberofiterations = 3*50*365 # number of calculations performed before result is presented
    # granularity * numberofiterations gives the timeframe simulated (in seconds)
userealplanets = "True"
randomplanetnumber = 8
useallplanets = 1 # 1 or True =use all planets with their data from nasa's list;
    # 0 or False = use only earth, moon, jupiter, saturn, venus (the ones with most effect on earth)
numberofruns = 1

noisiness = 200 # controls how often status is sent to terminal, and how often the main loop checks to pause if running on battery
vagrant_included = 1 # 1: throw a rogue brown dwarf at the inner solar system
vagrant_sattelites = 3 # number of planet-sized companions to that brown dwarf
blur = 0.2
displaystandards = "True"
interactivemode = "False"