from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
import sqlite3
from tkinter.messagebox import *

def add_product(product_no):
    conn = sqlite3.connect("store.sqlite")
    cur = conn.cursor()
    cur.execute('create table if not exists products'
                '(name text not null,'
                'no integer not null primary key,'
                'price text)')
    cur.execute('select name, price from products where no=?', (int(product_no), ))
    record = cur.fetchone()
    if record is None:
        html = session.get(f"https://www.amazon.in/s?k={product_no}")
        soup = BeautifulSoup(html.text, 'html.parser')
        title = soup.find("span", class_="a-size-base-plus a-color-base a-text-normal")
        if title is None:
            html = session.get(f"https://www.google.com/search?q={product_no}&tbm=shop")
            soup = BeautifulSoup(html.text, 'html.parser')
            title = soup.find("h4", class_="A2sOrd")
            if title is None:
                showerror("Error Found!", "No product found!!!")
                return
            price = soup.find("span", class_="a8Pemb")
            price = round(float(price.text.replace("₹", "")), 2)
        else:
            price = soup.select_one("span.a-text-price > span.a-offscreen")
            if price is None:
                price = soup.find("span", class_="a-price-whole")
            price = price.text.replace(",", "")
            price = int(price.replace("₹", ""))
        cur.execute('insert into products values'
                    '(?, ?, ?)', (title.text, int(product_no), str(price)))
        print("inserted")
        title = title.text
        quantity = re.findall("\(([0-9]+)\)$", title)
        if quantity:
            title = title.replace(" (" + quantity[0] + ")", "")
            price = round(price / quantity[0], 2)
    else:
        title = record[0]
        price = float(record[1])

    product_info = products.get(product_no, dict())
    product_info['name'] = product_info.get('name', title)
    product_info['count'] = product_info.get('count', 0) + 1
    product_info['price'] = round(product_info.get('price', price), 2)
    product_info['cost'] = round(product_info.get('price', price) * product_info['count'], 2)
    products[product_no] = product_info
    conn.commit()
    cur.close()
    conn.close()

session = HTMLSession()
products = dict()

