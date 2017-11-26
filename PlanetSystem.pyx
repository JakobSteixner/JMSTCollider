import numpy
import time
import subprocess as sb
from orbithelpers import *
import collider

class PSystem(list):
    global savefolder
    def __init__(self, List, name=None, folderlocation = None):
        self.savefolder = folderlocation
        self.name = name
        for planetary_object in List:
            self.append(planetary_object)
        self.getcentral()
        self.marked_for_deletion = []
        #self.central = [pobject for pobject in self if pobject.mass == max([plobject.mass for plobject in self])]
    def getcentral(self):
        # attribute currently not used
        self.central = [pobject for pobject in self if pobject.mass == max([plobject.mass for plobject in self])][0]
    def update(self, time, granularity, iterations=1):
        for iteration in xrange(iterations):
            for planetary_object in self:
                #print [otherplanet.position for otherplanet in self if not otherplanet is planetary_object]
                planetary_object.updatevelocity([otherplanet for otherplanet in self if not otherplanet is planetary_object], granularity)
            for planetary_object in self:
                planetary_object.updateposition(time, granularity)
    def addplanet(self, pplanet):
        self.append(pplanet)
        if pplanet.color == None:
                pplanet.color =  hexstring(random.randrange(16**6))
        self.getcentral()
    def makevelocitydataagearray(self, granularity):
        # dictionaries with key=planet.idnumber, entry=list
        # squared distances and relative velocities are easier to calculate than plain ones
        # that's why these are stored
        self.velocitydataages = {item.idnumber:[granularity for otheritem in self] for item in self}
        self.relvelocitiessquared = {thisobject.idnumber:[sum(abs(thisobject.velocity-otherobject.velocity)) for otherobject in self] for thisobject in self}
        self.distancessquared = {thisobject.idnumber:[sum(abs(thisobject.position-otherobject.position)) for otherobject in self] for thisobject in self}
    def updatearray(self, granularity, initialising=0, iterations=1):
        try: a = self.accelarray
        except AttributeError:
            #list version - might be reactivated if it turns out dict() is slower
            #self.accelarray = [[numpy.array([0,0,0]) for planobject in self] for planobject in self]
            #dict version
            self.accelarray = self.acceldict = {item.idnumber:[numpy.array([0,0,0]) for otherobject in self] for item in self}
            # only first dimension is implemented as a dictionary; we could make a dict
            # of dicts, but then we lose the ability to take sums
                  
        #print self.accelarray
        for i in xrange(iterations):
            if self.marked_for_deletion:
                for entry in self.marked_for_deletion:
                    self[self.marked_for_deletion[0][0]] = self[self.marked_for_deletion[1]]
                    self[self.marked_for_deletion[0][1]].mass = self[self.marked_for_deletion[0][1]].mass / 1e4
            for index in range(len(self)):
                planetary_object = self[index]
                for otherindex in range(index+1, len(self)):
                    otherobject = self[otherindex]
                    # complex condition- true if the relative speed of the two objects is such
                    # that they've moved more than 1/250 their distance since the last update
                    # if False, the last calculated value for their accelerations is re-used
                    # this is supposed to save computations at a low cost in terms of accuracy
                    # I'm unsure it actually saves much since it comes at the cost of massive
                    # list/dict lookup
                    if distance(planetary_object.position, otherobject.position) < min((distance(planetary_object.velocity, otherobject.velocity) * granularity * 5), (planetary_object.radius + otherobject.radius) * 2):
                        close_pass = collider.Collision(planetary_object, otherobject)
                        close_pass.calculate_close_pass()
                        if close_pass.hascollided == True:
                            #self[index] = close_pass.newobject
                            self.marked_for_deletion.append((index, otherindex), close_pass.newobject)
                            planetary_object.velocity, otherobject.velocity = [close_pass.newobject.velocity] * 2
                            # do something to make sure the
                        else:
                            pass # make sure at the end, during .updatevelocityfromarray, the more precise result of close_pass is used
                            # however that's supposed to work
                    complex_condition = (# relative velocity * granularity * 10000 < distance, i.e.
                                        self.relvelocitiessquared[planetary_object.idnumber][otherindex]
                                        ##* (granularity **2)
                                        * (250**2)
                                        * ((self.velocitydataages[planetary_object.idnumber][otherindex]) ** 2)
                                        ) > self.distancessquared[planetary_object.idnumber][otherindex]
                    #complex_condition = True
                    if initialising==1 or complex_condition==True:
                        mutualaccel = gravityaccelerationmutual(planetary_object, otherobject)
                        self.accelarray[planetary_object.idnumber][otherindex] = mutualaccel[0]
                        self.accelarray[otherobject.idnumber][index] = mutualaccel[1]
                        self.velocitydataages[planetary_object.idnumber][otherindex] = granularity
                        self.velocitydataages[otherobject.idnumber][index] = granularity
                        self.relvelocitiessquared[planetary_object.idnumber][otherindex] += sum(abs(planetary_object.velocity-otherobject.velocity))
                        self.distancessquared[planetary_object.idnumber][otherindex] += sum(abs(planetary_object.position-otherobject.position))
                    else:
                        #print "entering else branch for objects", planetary_object.name, otherobject.name
                        self.velocitydataages[planetary_object.idnumber][otherindex] += granularity
                        self.velocitydataages[otherobject.idnumber][index] += granularity
    
            for index,planobject in enumerate(self):
                self[index].updatevelocityfromarray(granularity, self.accelarray[planobject.idnumber])
                self[index]
            for index in range(len(self)):
                currentplanet = self[index]
                currentplanet.renewposition(granularity * currentplanet.velocity)
            
        #print [(someplanet.name, distance1(someplanet.position-self.central.position) / au) for someplanet in self]

    def savestatus(self, filename=None):
        if filename == None:
            filename = str("data_"+self.name+".txt")
        self.outfilename = filename
        print self.outfilename
        
        sb.call(('touch "%s"' % self.savefolder+"/"+self.outfilename), shell=True)
        outfile = file(self.savefolder+"/"+self.outfilename, "w")
        #print outfile
        for planetary_object in self:
            for eigenschaft in [planetary_object.name, planetary_object.mass, planetary_object.position, planetary_object.velocity]:
                outfile.write(str(eigenschaft))
                outfile.write("\t")
            outfile.write("\n")
        outfile.close()