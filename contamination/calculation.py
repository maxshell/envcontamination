from contamination.models import DVS
from contamination.models import Substance
from contamination.models import K7
from contamination.models import K4
from contamination.models import SpeedOfTransfer
from contamination.models import DepthZone
from contamination.models import Wind
from contamination.models import Temperature

from math import pow
import json

class Calculator():
  
  def __init__(self, dvs_id, substance_id, wind, temperature, mass):
    # Constants
    self.__height=0.05
    self.__result_multiplicator=1000
    self.__min_speed=1
    self.__max_speed=15
    # Temporary results
    self.__eqQuantInPrimCloud=None
    self.__eqQuantInSecCloud=None
    self.__timeOfEvaporation=None
    self.__depthZoneClouds=None
    self.__speedOfTransfer=None  
    # Parameters
    self.__k4=None   
    self.__k6=None
    self.__dvs=DVS.objects.get(id=dvs_id)
    self.__substance=Substance.objects.get(id=substance_id)  
    self.__wind=Wind.objects.get(speed=wind)
    self.__temperature=Temperature.objects.get(value=temperature)
    self.__k7=self.__substance.k7_set.get(temperature=temperature) 
    self.__mass=float(mass) 

  def calculate(self):
    self.updateWind()
    self.calcK4()
    self.calcEqQuantInPrimCloud()
    self.calcTimeOfEvaporation()
    self.calcK6()
    self.calcEqQuantInSecCloud()
    self.calcDepthZoneClouds()
    self.calcSpeedOfTransfer()
    return json.dumps({'radius':float(self.__depthZoneClouds), 
                       'speed':float(self.__speedOfTransfer)})
     
  def updateWind(self):
    if self.__wind.speed<self.__min_speed:
      self.__wind=Wind.objects.get(speed=self.__min_speed)
    elif self.__wind.speed>self.__max_speed:
      self.__wind=Wind.objects.get(speed=self.__max_speed)
    return self.__wind
  
  def calcK4(self):
    k4s=K4.objects.values_list('wind_speed', flat=True)
    closestSpeed=sorted(k4s, key=lambda x: abs(x-self.__wind.speed))[0]
    self.__k4=K4.objects.get(wind_speed=closestSpeed)
    return self.__k4

  def calcEqQuantInPrimCloud(self):
    self.__eqQuantInPrimCloud=(self.__substance.K1 * self.__substance.K3 *
                              self.__dvs.K5 * self.__k7.value_primary_cloud *
                              self.__mass)
    return self.__eqQuantInPrimCloud

  def calcTimeOfEvaporation(self):
    self.__timeOfEvaporation=((self.__height * self.__substance.density_liquid) /
                              (self.__substance.K2 * self.__k7.value_secondary_cloud *
                               self.__k4.value))
    self.__timeOfEvaporation=self.__timeOfEvaporation < 1 and 1 or self.__timeOfEvaporation
    return self.__timeOfEvaporation
  
  def calcK6(self):
    self.__k6 = pow(self.__timeOfEvaporation, 0.8)
    return self.__k6

  def calcEqQuantInSecCloud(self):
    self.__eqQuantInSecCloud=(((1 - self.__substance.K1) * self.__substance.K2 *
                              self.__substance.K3 * self.__k4.value * self.__dvs.K5 *
                              self.__k6 * self.__k7.value_secondary_cloud) *
                              (self.__mass / (self.__height * self.__substance.density_liquid)))
    return self.__eqQuantInSecCloud

  def calcDepthZoneClouds(self):
    eq_amounts=self.__wind.depthzone_set.values_list('equivalent_amount', flat=True)
    eqAmountPrim = sorted(eq_amounts, key=lambda x: abs(x-self.__eqQuantInPrimCloud))[0]
    eqAmountSec = sorted(eq_amounts, key=lambda x: abs(x-self.__eqQuantInSecCloud))[0]
    depthZonePrim=self.__wind.depthzone_set.get(equivalent_amount=eqAmountPrim)
    depthZoneSec=self.__wind.depthzone_set.get(equivalent_amount=eqAmountSec)
    self.__depthZoneClouds=(max(depthZonePrim.value, depthZoneSec.value) 
                            + (0.5 * min(depthZonePrim.value, depthZoneSec.value)))
    self.__depthZoneClouds=self.__depthZoneClouds * self.__result_multiplicator
    return self.__depthZoneClouds
  
  def calcSpeedOfTransfer(self):
    self.__speedOfTransfer=[]
    speedsOfTransfer=self.__dvs.speedoftransfer_set.filter(wind_speed=self.__wind.speed)
    if len(speedsOfTransfer)==0:
      for dvs in DVS.objects.all():
        speedsOfTransfer=self.__wind.speedoftransfer_set.filter(dvs=dvs)
        if len(speedsOfTransfer)>0: break
    
    if len(speedsOfTransfer)>0:
      self.__speedOfTransfer=speedsOfTransfer[0].value 
    else:
      self.__speedOfTransfer=0
    return self.__speedOfTransfer
           
    