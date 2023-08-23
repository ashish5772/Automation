
from bs4 import BeautifulSoup
import requests
import logging
logging.basicConfig()

a=requests.get(r'https://www.amazon.in/HyperX-HX-KB1BL1-NA-Mechanical-Gaming-Keyboard/dp/B01LWMXIRY/ref=sr_1_1?ie=UTF8&qid=1525586010&sr=8-1&keywords=hyperx+alloy+fps')

a.text
soup = BeautifulSoup(a.text, 'lxml')

soup.prettify()

section=soup.find('div',id='price')
priceline = section.find('span', id='priceblock_ourprice').text
import re
price = int(re.findall('[0-9]+[,]*[0-9]*',priceline)[0].replace(',',''))
import smtplib
s = smtplib.SMTP('smtp.gmx.com', 25)
s.set_debuglevel(1)
s.starttls()
mail = 'ashish577@gmx.com'
pwd='Nainwal@123'
to='ashish577@gmail.com'
subject=f'price is {price}'
msg = "From: {}\nTo: {}\nSubject: {} \n\n".format( mail, to, subject, 'low price' )
s.ehlo()
s.login(str(r"ashish577@gmx.com"), str(r"Nainwal@123"))
print(price)
if price<6000:
    s.sendmail(mail,to,msg)

