from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response

from django.utils import translation
from settings import LANGUAGES, LANGUAGE_CODE

from contamination.models import DVS
from contamination.models import Substance
from contamination.models import K7
from contamination.models import K4
from contamination.models import SpeedOfTransfer
from contamination.models import DepthZone
from contamination.models import Wind
from contamination.models import Temperature

from contamination.calculation import Calculator

AVAILABLE_LANGUAGES = [language[0].lower() for language in LANGUAGES]
DEFAULT_LANGUAGE=LANGUAGE_CODE 

def indexWithLanguage(request, language):
  if language in AVAILABLE_LANGUAGES:
    translation.activate(language)
  else:
    raise Http404
  dvss = DVS.objects.all()
  substances=Substance.objects.all()
  winds= Wind.objects.all()
  temperatures=Temperature.objects.all()
  return render_to_response('contamination/index.html', 
                            {'dvss' : dvss, 'substances' : substances,
                             'winds' : winds, 'temperatures' : temperatures,
                             'request' : request, 'language' : language })

def index(request):
  language=translation.get_language()
  language=language=="" and DEFAULT_LANGUAGE or language
  return indexWithLanguage(request, language)
 
def calculate(request, dvs_id, substance_id, wind, temperature, mass):
  wind=wind.replace(",",".")
  calculator=Calculator(dvs_id, substance_id, wind, temperature, mass)
  return HttpResponse(calculator.calculate())


  
  
  
  
