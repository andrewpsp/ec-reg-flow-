"""
 Copyright 2014, Yellow Pages Group Co.  All rights reserved.
 Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 1)	Redistributions of source code must retain a complete copy of this notice, including the copyright notice, this list of conditions and the following disclaimer; and
 2)	Neither the name of the Yellow Pages Group Co., nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT OWNER AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 Requires: Python 2.4+
 Version: 2.0.0 (2014-04-02)
"""
import json as simplejson
import urllib2
import urllib
import itertools
import unicodedata
import re


class YellowAPI(object):
	"""
	A thin wrapper around urllib2 to perform calls to YellowAPI.  This class
	does not do any processing of the response contents (XML or JSON).
	"""

	def __init__(self, uid, lang='en', handlers=[]):
		self.uid = uid
		self.lang = lang

		self.opener = urllib2.build_opener(*handlers)
		self.last_url = None

	def set_places_api_key(self, api_key, sandbox = True):
		if len(api_key) != 24:
			raise TypeError('api_key should be 24 characters.')

		self.places_api_key = api_key
		if sandbox:
			self.places_url = 'http://api.sandbox.yellowapi.com'
		else:
			self.places_url = 'http://api.yellowapi.com'

	def set_deals_api_key(self, api_key, sandbox = True):
		if len(api_key) != 24:
			raise TypeError('api_key should be 24 characters.')

		self.deals_api_key = api_key
		if sandbox:
			self.deals_url = 'http://deals.sandbox.yellowapi.com'
		else:
			self.deals_url = 'http://deals.yellowapi.com'


	def find_business(self, what, where, page=None, page_len=None,
			sflag=None):
		"""
		Perform the FindBusiness call.
		"""
		url = self._build_places_url('FindBusiness', what=what, where=where,
				pg=page, pgLen=page_len, sflag=sflag)
		return self._perform_request(url)


	def get_business_details(self, city, prov, bus_name, listing_id):
		"""
		Perform the GetBusinessDetails call.
		"""
		kws = {'prov': self.encode_info(prov), 'bus-name': self.encode_info(bus_name),
				'listingId': listing_id, 'city': self.encode_info(city)
				}
		url = self._build_places_url('GetBusinessDetails', **kws)
		return self._perform_request(url)


	def find_dealer(self, pid, page=None, page_len=None):
		"""
		Perform the FindDealer call.
		"""
		url = self._build_places_url('FindDealer', pid=pid, pg=page,
				pgLen=page_len)
		return self._perform_request(url)

	def get_type_ahead(self, usertext, fieldtype='WHAT'):
		"""
		Perform the GetTypeAhead call.
		"""
		url = self._build_places_url('GetTypeAhead', text=usertext, type=fieldtype)
		return self._perform_request(url)

	def find_deals_near(self,  what, lat, lng, page=None, page_len=None, dealtype='deal coupon', sflag=None, dist = 5):
		"""
		Perform the search/geo call.
		"""
		url = self._build_deals_url('search/geo/' + lat.strip() + '/' + lng.strip(), keyword=what, type=dealtype,
			pg = page, pgLen=page_len, sflag = sflag, radius = dist)
		return self._perform_request(url)

	def find_national_deals(self,  what, page=None, page_len=None, dealtype='deal coupon', sflag=None):
		"""
		Perform the search/national call.
		"""
		url = self._build_deals_url('search/national', keyword=what, type=dealtype,
			pg = page, pgLen=page_len, sflag = sflag)
		return self._perform_request(url)

	def find_merchant_deals(self, listing_id, page=None, page_len=None, dealtype='deal coupon', sflag=None):
		"""
		Perform the search/merchant call.
		"""
		url = self._build_deals_url('search/merchant/' + listing_id, type=dealtype,
			pg = page, pgLen=page_len, sflag = sflag)
		return self._perform_request(url)

	def get_deal_details(self, deal_id):
		"""
		Perform the deal call.
		"""
		url = self._build_deals_url('deal/' + deal_id)
		return self._perform_request(url)

	def get_coupon_details(self, coupon_id):
		"""
		Perform the deal call.
		"""
		url = self._build_deals_url('coupon/' + coupon_id)
		return self._perform_request(url)

	def get_deal_categories(self):
		"""
		Perform the deal call.
		"""
		url = self._build_deals_url('categories')
		return self._perform_request(url)

	def get_deal_content_types(self):
		"""
		Perform the deal call.
		"""
		url = self._build_deals_url('content-types')
		return self._perform_request(url)


	def get_last_query(self):
		"""
		Used for debugging purposes.  Displays the url string used in the
		last calls.
		"""
		return self.last_url

	NAME_PATTERN = re.compile('[^A-Za-z0-9]+')
	SEODASH_PATTERN = re.compile('\s+')
	@staticmethod
	def encode_info(name):
		"""
		Properly encode the business name for subsequent queries.
		"""
		normalized_string = YellowAPI.NAME_PATTERN.sub(' ', unicodedata.normalize('NFKD', name).encode('ascii','ignore')).strip()
		normalized_string = YellowAPI.SEODASH_PATTERN.sub('-', normalized_string)
		if (normalized_string == ''):
			return '-'
		else:
			return normalized_string

	def _build_deals_url(self, method, **kwargs):
		"""
		Build an HTTP url for the request.
		"""
		kwargs.update({'apikey': self.deals_api_key, 'lang' : self.lang, 'fmt': 'JSON', 'UID': self.uid})
		params = ["%s=%s" % (k,urllib.quote(str(v))) for (k,v) in itertools.ifilter(
				lambda (k,v): v is not None, kwargs.iteritems())]

		self.last_url = "%s/%s?%s" % (self.deals_url, method, "&".join(params))
		return self.last_url


	def _build_places_url(self, method, **kwargs):
		"""
		Build an HTTP url for the request.
		"""
		kwargs.update({'apikey': self.places_api_key, 'lang' : self.lang, 'fmt': 'JSON', 'UID': self.uid})
		params = ["%s=%s" % (k,urllib.quote(str(v))) for (k,v) in itertools.ifilter(
				lambda (k,v): v is not None, kwargs.iteritems())]

		self.last_url = "%s/%s/?%s" % (self.places_url, method, "&".join(params))
		return self.last_url

	def _perform_request(self, url):
		"""
		Perform the GET Request and handle HTTP response.
		"""
		print url
		resp = None
		try:
			resp = self.opener.open(url)
			body = resp.read()
		except urllib2.HTTPError, err:
			if err.code == 400:
				msg = err.read()
				err.msg += "\n" + msg
			raise(err)
		finally:
			if resp:
				resp.close()
		return body