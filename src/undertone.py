from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from pprint import pprint
import re
import time
import math
import numpy as np
from scipy import stats

auth = Oauth1Authenticator(
    consumer_key='',
    consumer_secret='',
    token='',
    token_secret=''
)
client = Client(auth)

#define hash table class
def hash_function(key_string, size):
    return sum([ord(c) for c in key_string]) % size

#class defined for a hash table 
class hash_table:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        #capacity is automatically set to 1000
        self.size = 0 #size initially set to 0
        self._keys = [] #define array of keys
        self.data = [[] for _ in range(capacity)]
        #same as a for loop appending empty lists in a list

    def _find_by_key(self, key, find_result_func):
        index = hash_function(key, self.capacity)
        hash_table_cell = self.data[index]
        found_item = None
        for item in hash_table_cell:
            if item[0] == key:
                found_item = item
                break
        return find_result_func(found_item, hash_table_cell)

    def insert(self, key, obj):
        def find_result_func(found_item, hash_table_cell):
            if found_item:
                found_item[1] = obj
            else:
                hash_table_cell.append([key, obj])
                self.size += 1
                self._keys.append(key)

        self._find_by_key(key, find_result_func)
        return self

    def get(self, key):
        def find_result_func(found_item, _):
            if found_item:
                return found_item[1]
            else:
                raise KeyError(key)
        return self._find_by_key(key, find_result_func)

    def delete(self, key):
        def find_result_func(found_item, hash_table_cell):
            if found_item:
                hash_table_cell.remove(found_item)
                self._keys.remove(key)
                self.size -= 1
                return found_item[1]
            else:
                raise KeyError(key)
        return self._find_by_key(key, find_result_func)

    def keys(self):
        return self._keys

    def __repr__(self):
        return '{ ' + ', '.join([key + ':' + str(self.get(key)) for key in self._keys]) + ' }'

class location:
	def __init__(self,neighborhood,city,county,state):
		self.neighborhood = neighborhood
		self.city = city
		self.county = county
		self.state = state
#classes/objects defined, functions run from main below


content_hash_table = hash_table(5000)
city_restaurant_hash_table = hash_table(5000)


def import_and_hash():
	citycountystate = []
	with open('statecountycity.txt') as f:
		citycountystate = f.readlines()
	info_array = []
	for ccs in citycountystate:
		ccs_array = ccs.split(',')
		info_piece = ['NULL',ccs_array[0],ccs_array[1],ccs_array[2]]
		info_array.append(info_piece)
	#pprint(info_array)

	data = ''
	n_info_array = []
	with open ("neighborhoods.txt", "r") as f:
	    data=f.read().replace('</li>\\n<li>', ',').replace('\\n                                    <ul class="bullet-list-round">\\n<li>','!!!').replace('</li>\\n</ul>\\n,','***')
	#pprint(data)
	neighborhoods = data.split('***')
	#splits by major city ^
	for hood in neighborhoods: # iterate through all the neighborhood cities
		split_array = hood.split('!!!') #split_array[1] is a list of neighborhoods delimited by commas
		cs_arr = split_array[0].split(', ') #splits into the city and state ID
		n_city = cs_arr[0] #city var
		n_state = cs_arr[1] #state var
		n_neighborhoods = split_array[1].split(',') #splits neighborhoods
		#pprint(n_city)

		#gets counties from statecountycity.txt and matches by comparing city names
		n_county = ''
		for x in info_array:
			if x[1] == n_city and x[3] == n_state:
				n_county = x[2]
				#pprint(n_county)
		for n in n_neighborhoods:
			n_info_piece = [n,n_city,n_county,n_state]
			n_info_array.append(n_info_piece)
	#pprint(n_info_array)

	info_array_f = info_array + n_info_array
	#pprint(info_array_f)
	#pprint('info_array_f created and formatted')
	for piece in info_array_f:
		location_instance = location(piece[0], piece[1], piece[2], piece[3])
		key = piece[0] + '#' + piece[1] + '#' + piece[2] + '#' + piece[3]
		#pprint(key)
		content_hash_table.insert(key, location_instance)
	#pprint('created content_hash_table')

	#hash table check TESTS
	#print(content_hash_table.get('West ViewMilwaukee"Milwaukee CountyWI'))
	return info_array_f


def handle_responses(location_arr):
	#params is for first page results
	#sort = 1 finds restaurants by distance, since we don't care about Best matched or Highest Rated
	params = {
    'term': 'seafood',
    'lang': 'en',
    'sort:': '1'
	}
	#param_offset represents the parameters needed to grab second page results
	params_offset = {
    'term': 'seafood',
    'lang': 'en',
    'limit': '20',
    'offset': '20',
    'sort:': '1'
	}
	#test obj
	location_instance = location(location_arr[0],location_arr[1],location_arr[2],location_arr[3])

	if location_instance.neighborhood != 'NULL':
		query = location_instance.neighborhood + ', ' + location_instance.city + ', ' + location_instance.state
	else:
		query = location_instance.city + ', ' + location_instance.state
	try:
		response = client.search(query, **params)
	except:
		response = []
	try:
		response_2 = client.search(query, **params_offset)
	except:
		response_2 = []

	first_20, second_20 = [],[]
	if response == []:
		first_20 = []
	else:
		for x in range(0, len(response.businesses)): #1st page
			first_20.append([response.businesses[x].id,response.businesses[x].location.city]) #append [Yelp Business ID, City of Business]
	if response_2 == []:
		second_20 = []
	else:
		for x in range(0, len(response_2.businesses)): #2nd page
			second_20.append([response_2.businesses[x].id,response_2.businesses[x].location.city]) 
	all_results = first_20 + second_20 #combine first page and second page results
	city_restaurants = [] #will hold Yelp Business ID's 

	for restaurant in all_results: #run through 40 formatted responses
		if location_instance.city == restaurant[1]: #check if the business is really in the city queried for
			city_restaurants.append(restaurant[0]) #append the Yelp Business ID to the city_restaurants array
	#pprint(city_restaurants)

	number = len(city_restaurants)

	key = location_instance.neighborhood + '#' + location_instance.city + '#' + location_instance.county + '#' + location_instance.state
	#pprint(key)
	city_restaurant_hash_table.insert(key, city_restaurants)
	return [key, number, location_instance.county, city_restaurants]

def rate(business_id_array):
	#total score for that city's restaurants for the particular cuisine
	score = 0
	#params speciifies only the english language
	params = {
    'lang': 'en'
	}
	#if no restaurants exist, then return a score of 0
	if len(business_id_array) == 0:
		score = 0
		return score
	else:
		#go through all the restaurants in the city
		for business_id in business_id_array:
			response = client.get_business(business_id, **params)

			try:
				#exponent is LOG(review_count), look at the project's paper for an explanation
				exponent = math.log(response.business.review_count)
			except AttributeError:
				#no reviews means review_count = 0 and the exponent is set to 0 to avoid a math error
				exponent = 1
			try:
				#set base to the rating of the restaurant
				base = response.business.rating
			except AttributeError:
				#no reviews means base = 0
				base = 0
			total = base ** (exponent)
			#add all totals to score
			#score is the number/value of restaurants for the city
			score += total
		return score

def percentage_of_area_under_std_normal_curve_from_zcore(z_score):
    return .5 * (math.erf(z_score / 2 ** .5) + 1)

def california():
	calif = []
	with open('california.txt') as f:
		calif = f.readlines()
	out_array = []
	for ccs in calif:
		cal_array = ccs.split(',')
		piece = [cal_array[0].replace('"',''),cal_array[1].replace(' ',''),cal_array[2].replace(' ','').replace('\n','')]
		out_array.append(piece)
	array_county = []
	for x in out_array:
		array_county.append(x[0])
	set_array_county = set(array_county)
	final_arr = []
	for county in set_array_county:
		divisor = 0
		total_score = 0
		for y in out_array:
			if county == y[0]:
				divisor += int(y[1])
				if divisor == 0:
					divisor = 1
				total_score += float(y[2])
		final_arr.append((total_score/divisor))
	pprint(final_arr)
	np_array = np.asarray(final_arr)
	zscore_arr = stats.zscore(np_array)

	fin = []
	for x in zscore_arr:
		num = percentage_of_area_under_std_normal_curve_from_zcore(x)
		fin.append(num)

	proj = zip(set_array_county,fin)
	for x in proj:
		print(x[0],x[1])



def main():
	info_array_f = import_and_hash()
	file = open("UNDERTONE-1.txt", "w")
	counter = 2702
	for x in range(2702,len(info_array_f)):
		line_cr = handle_responses(info_array_f[x])
		#pprint(line_cr)

		score = rate(line_cr[3])
		county = line_cr[2]
		num = line_cr[1]
		#add num to file so it can be used later for averages
		final_write = [county, num, str(score)]
		pprint(str(counter) + '      ' + str(final_write))

		file.write(', '.join([str(x) for x in final_write]))
		file.write('\n')
		#print(counter)
		counter+=1
	file.close()
	california()

start_time = time.time()
main()
print("--- %s seconds --- total time taken to run undertone.py" % (time.time() - start_time))

