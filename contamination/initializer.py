from django.http import HttpResponse

from contamination.models import DVS
from contamination.models import Substance
from contamination.models import K7
from contamination.models import K4
from contamination.models import SpeedOfTransfer
from contamination.models import DepthZone
from contamination.models import Wind
from contamination.models import Temperature

import os

def initialize(request):
  
  sourceFolder="./contamination/data"
  
  windsfh=open(os.path.join(sourceFolder, "winds.txt"), "rU")
  for line in windsfh:
    if line[-1]=="\n": line=line[:-1]
    Wind(speed=float(line)).save()
  windsfh.close()
    
  dvssfh=open(os.path.join(sourceFolder, "dvss.txt"), "rU")
  for line in dvssfh:
    if line[-1]=="\n": line=line[:-1]
    dvsData=line.split("\t")
    DVS(name=dvsData[0], name_ru=dvsData[1], name_uk=dvsData[2], 
        K5=float(dvsData[3]), K8=float(dvsData[4])).save()
  dvssfh.close()
   
  temperaturesfh=open(os.path.join(sourceFolder, "temperatures.txt"), "rU")
  for line in temperaturesfh:
    if line[-1]=="\n": line=line[:-1]
    Temperature(value=int(line)).save()
  temperaturesfh.close()
  
  substancesfh=open(os.path.join(sourceFolder, "substances.txt"), "rU")
  for line in substancesfh:
    if line[-1]=="\n": line=line[:-1]
    substData=line.split("\t")
    substance=Substance(name=substData[0],name_ru=substData[1], name_uk=substData[2], 
              density_liquid=float(substData[4]), 
              boiling_point=float(substData[5]), threshold_toxic_dose=float(substData[6]), 
              K1=float(substData[7]), K2=float(substData[8]), K3=float(substData[9]))
    if substData[3]!="no":
      substance.density_gas=float(substData[3])
    substance.save()
  substancesfh.close()
  
  k7sfh=open(os.path.join(sourceFolder, "k7s.txt"), "rU")
  for line in k7sfh:
    if line[-1]=="\n": line=line[:-1]
    k7Data=line.split("\t")
    K7(substance=Substance.objects.get(name=k7Data[0]), 
       temperature=Temperature.objects.get(value=int(k7Data[1])), 
       value_primary_cloud=float(k7Data[2]), value_secondary_cloud=float(k7Data[3])).save()
  k7sfh.close()
  
  k4sfh=open(os.path.join(sourceFolder, "k4s.txt"), "rU")
  for line in k4sfh:
    if line[-1]=="\n": line=line[:-1]
    k4Data=line.split("\t")
    K4(wind_speed=Wind.objects.get(speed=float(k4Data[0])), value=float(k4Data[1])).save()
  k4sfh.close()
  
  depthzonesfh=open(os.path.join(sourceFolder, "depthzones.txt"), "rU")
  for line in depthzonesfh:
    if line[-1]=="\n": line=line[:-1]
    dzData=line.split("\t")
    DepthZone(wind_speed=Wind.objects.get(speed=float(dzData[0])),
              equivalent_amount=float(dzData[1]), value=float(dzData[2])).save()
  depthzonesfh.close()
  
  speedsoftransferfh=open(os.path.join(sourceFolder, "speedsoftransfer.txt"), "rU")
  for line in speedsoftransferfh:
    if line[-1]=="\n": line=line[:-1]
    sotData=line.split("\t")
    SpeedOfTransfer(dvs=DVS.objects.get(name=sotData[0]),
                    wind_speed=Wind.objects.get(speed=float(sotData[1])),
                    value=int(sotData[2])).save()
  speedsoftransferfh.close()

  return HttpResponse("Initialized")