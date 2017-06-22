import pickle, cv2, sqlite3
import numpy as np
class BGRHist:
	def __init__(self, bins):
		self.bins = bins
	def describe(self, img):
		hist = cv2.calcHist([img], range(3), None, self.bins, [0, 256]*3)
		cv2.normalize(hist, hist)
		return hist.flatten()
class Searcher:
	def __init__(self, index):
		self.index = index
	def Search(self, query):
		results = {}
		for (id, feature) in self.index.items():
			results[id] = self.chi2_distance(feature, query)
		res = sorted([(v, id) for (id, v) in results.items()])[0]
		return res
	def chi2_distance(self, histA, histB, eps = 1e-10):
		# compute the chi-squared distance
		d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
			for (a, b) in zip(histA, histB)])
		# return the chi-squared distance
		return d
descriptor = BGRHist([8, 8, 8])
args = {}
args['index'] = 'index.pkl'
args['query'] = 't.jpg'
index = pickle.load(open(args['index'], 'rb'))
query = cv2.imread(args['query'], 1)
query = descriptor.describe(query)
print('Data loaded successfully. Running search...')
res = Searcher(index).Search(query)
print('Search completed')
conn = sqlite3.connect('MAL.db')
cur = conn.cursor()
cur.execute('SELECT * FROM ani_lst WHERE id=?', (res[1],))
anime = cur.fetchone()
img = cv2.imdecode(np.fromstring(anime[2], np.uint8), cv2.IMREAD_COLOR)
name = anime[1]
year = str(anime[3])
genres = anime[4]
restrict = anime[5]
print('Name:', name)
print('Year:', year)
print('Genres', genres)
print('Restrict:', restrict)
cv2.imshow('\n'.join([name, year, genres, restrict]), img)
cv2.waitKey(0)
cv2.destroyAllWindows()