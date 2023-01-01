from selenium import webdriver
from scrapy import Selector
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import psycopg2
from http.server import BaseHTTPRequestHandler, HTTPServer
from webdriver_manager.chrome import ChromeDriverManager


hostName="localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    global data
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><meta charset=\"UTF-8\"></head>", "utf-8"))
        # self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        for i in data:
            self.wfile.write(bytes("<p>"+i[1]+"</p>", "utf-8"))
            self.wfile.write(bytes('<img src='+i[2]+'>', "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-setuid-sandbox")
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))


conn = psycopg2.connect(
    host="localhost", #localhost
    dbname="demo_database",
    user="postgres",
    password="4029862505",
    port=5432
)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS seznam')

query = "CREATE TABLE IF NOT EXISTS seznam (id int PRIMARY KEY,text varchar(40) NOT NULL,image_url varchar(120))"
cur.execute(query)
insert_script = 'INSERT INTO seznam (id, text, image_url) VALUES (%s, %s, %s)'
#connect to database

j=1
data=[]
URL = "https://www.sreality.cz/hledani/prodej/byty"
driver.get(URL)

sel = Selector(text=driver.page_source)
for n in range(1,21):
    nazov = sel.css('#page-layout > div.content-cover > div.content-inner > div.transcluded-content.ng-scope > div > div > div > div > div:nth-child(4) > div > div:nth-child('+str(n)+') > div > div > span > h2 > a > span::text').get() #It is also working
    image_url = sel.css('#page-layout > div.content-cover > div.content-inner > div.transcluded-content.ng-scope > div > div > div > div > div:nth-child(4) > div > div:nth-child('+str(n)+') > preact > div > div._2xzMRvpz7TDA2twKCXTS4R > a:nth-child(1) > img').xpath('@src').get()
    data.append((j, nazov, image_url))
    j+=1

for i in range(2,26):
    URL = "https://www.sreality.cz/hledani/prodej/byty?strana=" + str(i)
    driver.get(URL)

    sel = Selector(text=driver.page_source)
    for n in range(1,21):
        nazov = sel.css('#page-layout > div.content-cover > div.content-inner > div.transcluded-content.ng-scope > div > div > div > div > div:nth-child(4) > div > div:nth-child('+str(n)+') > div > div > span > h2 > a > span::text').get() #It is also working
        image_url = sel.css('#page-layout > div.content-cover > div.content-inner > div.transcluded-content.ng-scope > div > div > div > div > div:nth-child(4) > div > div:nth-child('+str(n)+') > preact > div > div._2xzMRvpz7TDA2twKCXTS4R > a:nth-child(1) > img').xpath('@src').get()
        data.append((j, nazov, image_url))
        j+=1

print(data)

for record in data:
    cur.execute(insert_script,record)
cur.execute('SELECT * FROM seznam')
a = cur.fetchall()

print(a)

hostname="localhost"
webServer = HTTPServer((hostName, serverPort), MyServer)
print("Server started http://%s:%s" % (hostName, serverPort))

try:
    webServer.serve_forever()
except KeyboardInterrupt:
    pass

webServer.server_close()
print("Server stopped.")

conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

