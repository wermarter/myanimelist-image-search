from lxml import html
import requests, sqlite3, re

def Process(url):
	id = int(re.findall('/([0-9]+)/.*?$', url)[0])
	if (id in id_fetched):
		print('Skiping ', id)
		return
	page = requests.get(url + '/userrecs')
	tree = html.fromstring(page.content)
	try:
		name = tree.xpath('//span[@itemprop="name"]/text()')[0]
	except:
		return
	print(id, name)
	try:
		img_url = tree.xpath('//img[@itemprop="image"]/@src')[0]
		img = sqlite3.Binary(requests.get(img_url, stream=True).content)
	except:
		img = None
	year = re.findall('<span class="dark_text">Aired:</span>\n.*([0-9][0-9][0-9][0-9]).*\n', page.text)
	try:
		year = int(year[0])
	except:
		year = 0
	genres = ''
	tmp = re.findall('<span class="dark_text">Genres:</span>\n(.*)</div>', page.text)[0]
	for item in re.findall('>(.*?)<', tmp):
		genres += item
	restrict = re.findall('<span class="dark_text">Rating:</span>\n(.*?)\n', page.text)[0].replace('amp;', '').strip()
	cur.execute('INSERT INTO ani_lst VALUES (?, ?, ?, ?, ?, ?)', (id, name, img, year, genres, restrict))
	for recc in re.findall('<a href="/anime/([0-9]+)/.*?" class="hoverinfo_trigger"', page.text):
		cur.execute('INSERT INTO userrecs VALUES (?, ?)', (id, recc))
	conn.commit()
	id_fetched.append(id)

conn = sqlite3.connect('MAL.db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS ani_lst (id INTEGER UNIQUE, name TEXT UNIQUE, img BLOB, year INTEGER, genres TEXT, restrict TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS userrecs (from_id INTEGER, to_id INTEGER)')
cur.execute('SELECT id FROM ani_lst')
id_fetched = []
for item in cur.fetchall():
	id_fetched.append(item[0])
threshold = 8000
p = len(id_fetched)
while (p < threshold):
	page = requests.get('https://myanimelist.net/topanime.php?limit={}'.format(p))
	print('Processing ', p, '/', threshold)
	tree = html.fromstring(page.content)
	for i in tree.xpath('//a[@class="hoverinfo_trigger fl-l fs14 fw-b"]/@href'):
		Process(i)
	p += 50
cur.close()
conn.close()