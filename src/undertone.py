from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from pprint import pprint
import re
import time

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
content_hash_table = hash_table(1000)

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
	#pprint('info_array_f created and formatted')
	for piece in info_array_f:
		location_instance = location(piece[0], piece[1], piece[2], piece[3])
		key = piece[0] + piece[1] + piece[2] + piece[3]
		#pprint(key)
		content_hash_table.insert(key, location_instance)
	#pprint('created content_hash_table')

	#hash table check TESTS
	#print(content_hash_table.get('West ViewMilwaukee"Milwaukee CountyWI'))


def handle_responses():
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
	location_instance = location('NULL', 'Cupertino', 'Santa Clara County', 'CA')

	if location_instance.neighborhood != 'NULL':
		query = location_instance.neighborhood + ', ' + location_instance.city + ', ' + location_instance.state
	else:
		query = location_instance.city + ', ' + location_instance.state
	response = client.search(query, **params)
	response_2 = client.search(query, **params_offset)

	first_20, second_20 = [],[]
	for x in range(0, len(response.businesses)): #1st page
		first_20.append([response.businesses[x].id,response.businesses[x].location.city]) #append [Yelp Business ID, City of Business]
	for x in range(0, len(response_2.businesses)): #2nd page
		second_20.append([response_2.businesses[x].id,response_2.businesses[x].location.city]) 
	all_results = first_20 + second_20 #combine first page and second page results
	city_restaurants = [] #will hold Yelp Business ID's 
	for restaurant in all_results: #run through 40 formatted responses
		if location_instance.city == restaurant[1]: #check if the business is really in the city queried for
			city_restaurants.append(restaurant[0]) #append the Yelp Business ID to the city_restaurants array
	pprint(city_restaurants)


def main():
	#import_and_hash()
	handle_responses()

start_time = time.time()
main()
print("--- %s seconds --- total time taken to run undertone.py" % (time.time() - start_time))

