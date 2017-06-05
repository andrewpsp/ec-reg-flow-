# Create your views here.
import json as simplejson
import urllib
from django.template import Context, loader
from django.http import HttpResponse
from YellowAPI import YellowAPI

deals_api_key = ''
places_api_key = ''
yellowAPI = YellowAPI('', [])
yellowAPI.set_places_api_key(places_api_key, True)
yellowAPI.set_deals_api_key(deals_api_key, True)

def index(request):
	t = loader.get_template('index.html')
	c = Context()

	return HttpResponse(t.render(c))

def search(request):
	# Get the field value from the search form
	what = request.GET.get('what', '')
	where = request.GET.get('where', '')

	# Fetch search results
	result = yellowAPI.find_business(what, where, 1, 40)

	t = loader.get_template('listing.html')
	c = Context({
		'result': simplejson.loads(result)	# Parse the result as a JSON Object
	})

	return HttpResponse(t.render(c))

def searchdeals(request):
	# Get the field value from the search form
	what = request.GET.get('what', '')
	latlng = request.GET.get('where', '').split(',')
	dealtype = request.GET.get('dealtype', 'deal coupon')

	# Fetch search results
	result = yellowAPI.find_deals_near(what, latlng[0], latlng[1], 1, 40)

	t = loader.get_template('listing_deals.html')
	c = Context({
		'result': simplejson.loads(result)	# Parse the result as a JSON Object
	})

	return HttpResponse(t.render(c))

def details(request, id):
	prov = request.GET.get('prov', '')
	city = request.GET.get('city', '')
	bus_name = request.GET.get('bus_name', '')

	# Fetch merchant details
	result = yellowAPI.get_business_details(city, prov, bus_name, id)
	details_json = simplejson.loads(result)

	# Pull deals if needed and allowed
	if details_json['Deal'] and deals_api_key:
		dealresult = yellowAPI.find_merchant_deals(id)
		deals_json = simplejson.loads(dealresult)
	else:
		deals_json = None

	t = loader.get_template('details.html')
	c = Context({
		'result': details_json,	# Parse the result as a JSON Object
		'dealresult': deals_json
	})

	return HttpResponse(t.render(c))

def urlencode(data):
   return urllib.urlencode(data)
