import matplotlib.pyplot as plt
import numpy
import subprocess as sb

def display_xcentric(reference_frame,
                     otherobjects,
                     xsize = 7000000000000,
                     ysize = 7000000000000, 
                     name=None, savepath=None,
                     timerange=None,
                     orientation=(0,1)):
    """Displays the trajectories of the planets in a system from one planet/star's reference frame
    refernce_frame: planet class object
    otherobjects: PSystem object or list of planet class objects
    xsize, ysize: distance range to be displayed
    name: determines the graph title and name of saved file
    savepath: folder path
    timerange: range which to display, allows trajectories for less than the whole period simulated
    orientation: orientation of the projection (e.g. (0,1) to project on the x,y-plane, (1,2) to project on y,z)
    """   
    if savepath == None:
        global savefolder
    else:
        savefolder  = savepath
    if ysize == xsize:
        plt.axis("equal")
    if name == None:
        name = "Trajectories relative to %s" % reference_frame.name
    plt.title(name)
    name = name.replace(" ","_")
    plt.ylim(-ysize, ysize)
    plt.xlim(-xsize, xsize)
    plt.plot([0],[0], "y.")
    otherobjects = list(otherobjects)
    try:
        otherobjects.remove(reference_frame)
    except ValueError:
        pass
    #if reference_frame in otherobjects:
    #    otherobjects = [otherobject for otherobject in otherobjects if otherobject != reference_frame]
    print "***now plotting sun***"
    for given_planet in otherobjects:
        print "computing distances for ", given_planet.name, reference_frame.name
        thispositions = numpy.array(given_planet.positionarchive)
        #print given_planet.name, thispositions
        #if given_planet.name == "Sun":

        if len(reference_frame.positionarchive) > len(thispositions):
            suntocurrent = reference_frame.positionarchive[-len(thispositions):]
            print "warning: central has longer archive than", given_planet.name
        elif len(reference_frame.positionarchive) < len(thispositions):
            thispositions = thispositions[-len(reference_frame.positionarchive):]
            suntocurrent = reference_frame.positionarchive
            print "warning: central has shorter archive than", given_planet.name
        else:
            suntocurrent = reference_frame.positionarchive
        if timerange == None:
            pass
        else:
            suntocurrent = suntocurrent[timerange[0]:timerange[1]]
            thispositions = thispositions[timerange[0]:timerange[1]]
        if given_planet.mass > 1e28:
            thismarker = "."
            
        else: thismarker = ","
        # exec(given_planet.name+"_sundistances= thispositions-suntocurrent", locals())
        # plt.plot((eval(given_planet.name+"_sundistances"))[:,orientation[0]], (eval(given_planet.name+"_sundistances"))[:,orientation[1]], color=given_planet.color, marker=thismarker, label=given_planet.name
        toplot = thispositions-suntocurrent
        plt.plot(toplot[:,orientation[0]],toplot[:,orientation[1]], color=given_planet.color, marker=thismarker, label=given_planet.name)
        #except ValueError: pass
    plt.legend(loc="lower left", fontsize=8)
    outputfilename = savefolder+"/orbits_%s-centric%s" % (reference_frame.name, name) + savefolder+".png"
    plt.ylabel("Distance (meters) from %s" % reference_frame.name)
    plt.xlabel("Distance (meters) from %s" % reference_frame.name)
    plt.savefig(outputfilename)
    plt.close()
    sb.call(('open "%s"' % outputfilename), shell=True)

def display_distances(reference_frame, otherobjects, logscale=True, name=None, savepath=None, legendlocation="upper right", sampling_rate=None,timerange=None):
    # parse optional arguments, insert defaults
    if timerange == None:
        timerange = (0, len(reference_frame.positionarchive))
    if name == None:
        name = "Distances from " + reference_frame.name
    plt.title(name) # print the name nicely on the graph
    name = name.replace(" ","_") # remove empty spaces before using the name for saving
    if logscale:
        plt.yscale("log")    
    if savepath==None:
        global savefolder
    else: savefolder = savepath
    outfilelocation = savefolder+"/"+name+".png"
    
    #make sure the central/reference frame is not in otherobjects-list
    otherobjects = list(otherobjects) # need to make a copy not to remove the central from the system globally
    try: otherobjects.remove(reference_frame)
    except ValueError: pass
    print otherobjects
    for given_planet in otherobjects:
        plt.plot(numpy.sum((given_planet.positionarchive-reference_frame.positionarchive)[timerange[0]:timerange[1]]**2,1)**0.5, color=given_planet.color, label=given_planet.name)
    plt.legend(loc=legendlocation, fontsize=8)
    plt.ylabel("Distance (meters) from %s" % reference_frame.name)
    try:
        plt.xlabel("Time (seconds * %s)" % sampling_rate)
    except NameError: pass 
    plt.savefig(outfilelocation)
    plt.close()
    sb.call((["open", outfilelocation]))
 