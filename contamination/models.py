from django.db import models

class DVS(models.Model):
  name=models.CharField(max_length=20, unique=True)
  # Dirty hack because of GAE doesn't support dbgettext:(
  name_ru=models.CharField(max_length=20, unique=True)
  name_uk=models.CharField(max_length=20, unique=True)
  K5=models.FloatField()
  K8=models.FloatField()
  
  def __unicode__(self):
    return self.name
  
class Substance(models.Model):
  name=models.CharField(max_length=100, unique=True)
  # Dirty hack because of GAE doesn't support dbgettext:(
  name_ru=models.CharField(max_length=100, unique=True)
  name_uk=models.CharField(max_length=100, unique=True)
  density_gas=models.FloatField(null=True)
  density_liquid=models.FloatField()
  boiling_point=models.FloatField()
  threshold_toxic_dose=models.FloatField()
  K1=models.FloatField()
  K2=models.FloatField()
  K3=models.FloatField()
  
  def __unicode__(self):
    return self.name

class Wind(models.Model):
  speed=models.FloatField(primary_key=True)
  
  def __unicode__(self):
    return unicode(self.speed)

class Temperature(models.Model):
  value=models.IntegerField(primary_key=True)
  
  def __unicode__(self):
    return unicode(self.value)
  
  
class K7(models.Model):
  substance=models.ForeignKey(Substance)
  temperature=models.ForeignKey(Temperature)
  value_primary_cloud=models.FloatField()
  value_secondary_cloud=models.FloatField()
  
  class Meta:
    unique_together = ("substance", "temperature")
  
  def __unicode__(self):
    return unicode("Substance: {0}  Temperature: {1}  Primary: {2}  Secondary: {3}"
                   .format(self.substance, self.temperature, 
                           self.value_primary_cloud, self.value_secondary_cloud))
  
class K4(models.Model):
  wind_speed=models.OneToOneField(Wind)
  value=models.FloatField()
  
  def __unicode__(self):
    return unicode(self.value)
  
class SpeedOfTransfer(models.Model):
  dvs=models.ForeignKey(DVS)
  wind_speed=models.ForeignKey(Wind)
  value=models.IntegerField(null=True)
  
  class Meta:
    unique_together = ("dvs", "wind_speed")
  
  def __unicode__(self):
    return unicode(self.value)
  
class DepthZone(models.Model):
  wind_speed=models.ForeignKey(Wind)
  equivalent_amount=models.FloatField()
  value=models.FloatField()
  
  class Meta:
    unique_together = ("wind_speed", "equivalent_amount")
  
  def __unicode__(self):
    return unicode(self.value)
  