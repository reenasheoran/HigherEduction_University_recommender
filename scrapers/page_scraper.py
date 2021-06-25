import urllib.request

site_url = "http://thegradcafe.com/survey/index.php?q=u%2A&t=a&pp=250&o=d&p={0}"
DIR = './scraped_htmls/'

if __name__ == '__main__':
    for i in range(1,2425):
        url_handle = urllib.request.urlopen(site_url.format(i))
        html = url_handle.read()
        html = html.decode('latin-1')
        filename = "{destination_dir}/{urlpage}.html".format(destination_dir=DIR,urlpage=str(i))
        with open(filename, 'wb') as file:
            file.write(html.encode('UTF-8'))
        print("extracted page: {0}".format(i))
 