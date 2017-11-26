import string, numpy
from Gconst import *

def distance(position1, position2):
    if not (len(position1) == 3 and len(position2) == 3):
        raise ValueError
    else:
        return ((position1[0] - position2[0])**2 + (position1[1] - position2[1])**2 + (position1[2] - position2[2])**2)**(0.5)

def distance1(vector):
    return sum(vector**2)**(0.5)

def distance2(position1, position2):
    return sum((position1-position2)**2)**0.5
    
def getvector(pos1, pos2):
    position1, position2 = pos1, pos2
    if not (len(position1) == 3 and len(position2) == 3):
        raise ValueError
    try: return position1-position2 # if input is numpy array
    except ValueError: # if input is list, still returnss correct result as array
        #print [float(position1[i]-position2[i]) for i in range(3)]
        #exit()
        return numpy.array([float(position1[i]-position2[i]) for i in xrange(3)])


def getdirectional_component(vector):
    return numpy.array(vector/distance1(vector))

def gravitypull(object1, object2):
    return object1.mass * object2.mass / (distance2(object1.position, object2.position)**2) * Gconstant

def gravityacceleration(object1, object2): #probably not needed anymore
    return gravitypull(object1, object2)/ object1.mass

def gravityaccelerationmutual(object1, object2):
  #if object1.name == "Sun":
    #print object1.name, object1.position
    #print object1.position - object2.position
    #print sum((object1.position-object2.position)**2)**0.5
    #gravpull = gravitypull(object1,object2) # = object1.mass * object2.mass * Gconstant / (getvector(object1.position, object2.position)**2)
    #print gravpull
    # gravitational force = mass1 * mass2 * Gconstant / (distance(object1, object2) squared)
    # grav. accelaration on either object: grav. force / mass
    # thus, acceleration is otherobject.mass * Gconstant / distancesquared
    distancesquared = sum((object1.position-object2.position)**2)
    direction = getdirectional_component(getvector(object1.position, object2.position))
    #print ((object2.mass * Gconstant * direction) / distancesquared, (object1.mass *  Gconstant * direction / distancesquared))
    return ((object2.mass * Gconstant * (-direction)) / distancesquared, (object1.mass *  Gconstant * (direction) / distancesquared))


def newvelocity(object1,object2, granularity=1):
    #print object1.velocity
    #print gravityacceleration(object1, object2)[0]
    #print getdirectional_component(object2.position - object1.position)
    object1.velocity = object1.velocity + granularity * gravityacceleration(object1, object2) * getdirectional_component(object2.position - object1.position)
   

def newvelocity1(object1,otherobjects, granularity=1):
    #print object1.velocity
    #print gravityacceleration(object1, object2)[0]
    #print getdirectional_component(object2.position - object1.position)
    object1.velocity = object1.velocity + granularity * sum([gravityacceleration(object1, object2) * getdirectional_component(object2.position - object1.position) for object2 in otherobjects])
    #object2.velocity = object2.velocity + granularity *  gravityacceleration(object1, object2)[1] * getdirectional_component(object1.position - object2.position)
    
def relvelocity(velocity1, velocity2):
    return sum((velocity1-velocity2)**2)**0.5

def zeropad(number, numberofdigits=None):
    """helper function for hexstring() below"""
    if type(number) == type("string"):
        inputnumber = number
    else:
        inputnumber = str(number)
    if numberofdigits == None:
        numberofdigits = len(inputnumber)
    inputlength = len(inputnumber)
    if inputlength > numberofdigits:
        raise ValueError("number too high")
    else:
        return (numberofdigits-inputlength) * "0" + inputnumber

def hexstring(number):
    hexstring = string.upper(hex(number)[2:])
    return "#"+zeropad(hexstring, 6)
