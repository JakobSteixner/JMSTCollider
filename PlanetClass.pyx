# -*- coding: utf-8 -*-

import numpy, random
from orbithelpers import *
from numpy import log, e, pi, log10
from math import cos, sin, atan2
from Gconst import *

    

class planet():
    def __init__(self,  name,  mass,  position=numpy.array([0,0,0]),  velocity=numpy.array([0,0,0]),   color=None, parent=None,  idnumber = None,  inclination = None, radius=None):
        self.mass=mass
        if radius == None: # derive radius from mass, assuming metallic-rocky composition slightly lighter than earth's
            volume = mass / 4500 #asummes density of 4.5 kg/cm\3
            radius = (volume / 4) ** (1.0/3)
        self.radius = radius
        self.idnumber = id(self)
        # 3-dimensional coordinates
        if (any(position+velocity) #second part of condition needs to become superfluous
            or name == "Sun"):
            self.position=numpy.array([float(i) for i in position])
            self.velocity=numpy.array([float(i) for i in velocity])
        else:
            set_orbit_parameters(self, inclination, distance)
        if color == None:
            self.color = hexstring(random.randrange(16**6))
        else: self.color = color
        self.positionarchive = [] #don't forget to convert into array for presentation
        self.velocityarchive = [] #same here
        self.name = name #string
        self.transits = [] #not currently used, can be deduced from positiondata if needed
        self.filename = self.name + ".txt" # outputfile for position data
        try:
            self.original_distance = distance1(self.position, self.parent.position)
        except AttributeError:
            pass # when a `Planet' doesn't have a parent, i.e. it is the central object
    def makecentral(self, planet_system_object):
        if self in planet_system_object:
            planet_system_object.central = self
            self.is_central = True
        else:
            print self.name, "not in system"
            raise IndexError
    def setparent(self, central_object):
        self.parent = central_object
    def updatevelocity(self, otherobjectarray, granularity=1):
        ##print moon.velocity
        #for otherobject in otherobjectarray:
        #    if distance(self.position, otherobject.position) < granularity * 3 / relvelocity(self.velocity, otherobject.velocity):
        #        print "****"
        #        print "collision imminent between", self.name, otherobject.name
        #        print "****"
        self.velocityarchive.append(copy.copy(self.velocity))
        #for plan_object in otherobjectarray:
            #oldothervelocity = copy.copy(otherobject.velocity)
        newvelocity1(self, otherobjectarray, granularity)
        #print moon.velocity
        #self.position = self.position + (self.velocity + oldvelocity) / 2 * granularity
        #otherobject.position = otherobject.position + (otherobject.velocity + oldothervelocity)/2 * granularity
    def updateposition(self, time, granularity=1):
        #self.position = self.position + (self.velocity + self.oldvelocity) / 2 * granularity
        self.positionarchive.append(self.position)
        self.position = self.position + self.velocity * granularity
        if (self.position[0]-sun.position[0]) * (self.positionarchive[-1][0]-sun.positionarchive[-1][0]) < 0 and self.position[1] < sun.position[1]:
            self.transits.append(time)
    def updatepositionfromarray(self, time, granularity):
        # not implemented
        pass
    def updatevelocityfromarray(self, granularity,accelarray1dim):
        self.velocity += sum(accelarray1dim) * granularity
        #print self.velocity
    def renewposition(self, vector):
        self.position = self.position + vector
        self.positionarchive.append(self.position)
        
class DeriveOrbitParameters():
    def __init__(self, distance, inclination, central_mass, excentricity=0):
        """current implementation approximately correct for low inclinations only!!!"""
        ascending_node_angle = random.uniform(0,2*pi)
        ascending_node_z = 0 # for as long as other planes than xy are not implemented
        ascending_node = numpy.array([sin(ascending_node_angle), cos(ascending_node_angle), ascending_node_z]) * distance
        angle_from_node = random.uniform(0,2*pi)
        azimuth = current_pos_planar_angle = ascending_node_angle + angle_from_node
        # good approximation for low inclinations, wildly off for extreme inclinations
        altitude = sin(angle_from_node) * inclination # this one's exact
        self.position = current_pos = numpy.array([cos(current_pos_planar_angle), sin(current_pos_planar_angle), altitude]) * distance
        abs_velocity = (Gconstant * central_mass / distance)**0.5
        z_relative_velocity = inclination * cos(angle_from_node) # still exact
        print "relative velocity along z acaxis, should be <1", z_relative_velocity
        z_absolute_velocity = abs_velocity * z_relative_velocity
        xy_relative_velocity = (1.-z_relative_velocity**2)**0.5
        # the following is where it gets inprecise for high inclinations: Requirements:
        # - at 0 inclination the old formula should be correct 
        # - at angle_from_node == pi/2 and angle_from_node = 0, the below is correct for all inclinations
        # - for other values, the x and y component of the xy planar direction need to be adjusted,
        #   such that, e.g. with inclination pi/2, angle_from_node pi/2, node at 0, y gets the whole
        #   load instead of x
        # potential replacement(?):
        # formula: θ = atan2( sin Δλ * cos φ2 , cos φ1 * sin φ2 − sin φ1 * cos φ2 * cos Δλ )
        # where	φ is latitude, λ is longitude
        # Δλ = angle_from node; φ2 = 0
        #  θ = atan2( sin angle_from_node * 1 , cos φ1 * 0 − sin φ1 * 1 * cos Δλ )
        #  θ = atan2( sin angle_from_node, − sin altitude * cos angle_from_node )
        #
        #
        #spher_bearing = atan2(sin(angle_from_node), sin(altitude) * cos(angle_from_node))
        #print "bearing on sphere",  spher_bearing
        x_velocity = xy_relative_velocity * cos(azimuth+pi/2) * abs_velocity
        y_velocity = xy_relative_velocity * sin(azimuth+pi/2) * abs_velocity
        self.velocity = velocity_tuple = numpy.array((x_velocity, y_velocity, z_absolute_velocity))
    def get_parameters(self):
        return (self.position, self.velocity)
        #return self.position, self.velocity

def get124(number):
   if number == 0:
     return 1
   else:
     return get124(number-1) ** number + 2 - number


class RandomPlanet():
    def __init__(self,
                 name,
                 parent,
                 distancerange = (0.2 * au ,25 * au), # only logarithmic
                 inclinationrange=0.1,
                 excentricityrange=0.1, # only linear
                 systemmainplane=((0,0,0),(0,0,0),(0,0,0)),
                 massrange=(1e22,1e28),
                 massdistributionlog=True
                ):
        self.inclination = random.uniform(0, inclinationrange)
        self.setmass(massrange, massdistributionlog)
        self.setdistance(distancerange)
        orbitparas = DeriveOrbitParameters(self.distance, self.inclination,parent.mass)
        position, velocity = orbitparas.position+parent.position, orbitparas.velocity+parent.velocity
        self.planet = planet(name, self.mass, position, velocity)
        print type(self)
    def setmass(self, massrange, massdistributionlog):
        masslowerlimit, massupperlimit = massrange
        if massdistributionlog==True:
            masslowerlimitlog, massupperlimitlog = log10(masslowerlimit), log10(massupperlimit)
            print masslowerlimit, massupperlimit, masslowerlimitlog, massupperlimitlog
            # no idea why, but log10 seems to be faster than log2 and more accurate than log
            self.mass = 10 ** random.uniform(masslowerlimitlog, massupperlimitlog)
        else:
            self.mass = random.uniform(masslowerlimit, massupperlimit)
    def setdistance(self, distancerange):
        lowerlimit, upperlimit = log10(numpy.array(distancerange))
        self.distance = 10**random.uniform(lowerlimit, upperlimit)


def makeasteroid(name, parent,astdistancerange):
    return RandomPlanet(name, parent, distancerange=astdistancerange, inclinationrange=0.07, massrange = (10e12, 10e19)).planet
