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
	    data=f.read().replace('</li>\\n<li>', ',').replace('\\n                                    <ul class="bullet-list-round">\\n<li>','!!!').replace('</li>\\n</ul>\\n,','***').replace("\\'","'").replace('\xef\xbb\xbf<ul class="bullet-list-round">\\n<li>','').replace('</li>\\n</ul>\\n</li>\\n</ul>\\n</li>\\n</ul>\\n</ul>\r','')
	#pprint(data)
	neighborhoods = data.split('***')
	for hood in neighborhoods:
		split_array = hood.split('!!!')
		cs_arr = split_array[0].split(', ')
		n_city = cs_arr[0]
		n_state = cs_arr[1]
		n_neighborhoods = split_array[1].split(',')
		#pprint(n_city)
		n_county = ''
		for x in info_array:
			if x[1] == n_city:
				n_county = x[2]
				#pprint(n_county)
		for n in n_neighborhoods:
			n_info_piece = [n,n_city,n_county,n_state]
			n_info_array.append(n_info_piece)
	#pprint(n_info_array)

	info_array_f = info_array + n_info_array
	pprint('info_array_f created and formatted')
	for piece in info_array_f:
		location_instance = location(piece[0], piece[1], piece[2], piece[3])
		key = piece[0] + piece[1] + piece[2] + piece[3]
		#pprint(key)
		content_hash_table.insert(key, location_instance)
	pprint('created content_hash_table')

	#hash table check TESTS
	#print(content_hash_table.get('West ViewMilwaukee"Milwaukee CountyWI'))


def handle_responses():
	params = {
    'term': 'food',
    'lang': 'en'
	}

	#response = client.search('San Francisco', **params)
	#for x in range(0, len(response.businesses)):
	#	print(response.businesses[x].name)

def main():
	import_and_hash()
	#handle_responses()

start_time = time.time()
main()
print("--- %s seconds --- total time taken to run undertone.py" % (time.time() - start_time))

