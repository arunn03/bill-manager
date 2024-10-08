from tkinter import *
from tkinter import ttk
from datetime import datetime
from barcode_reader import *
import keyboard
import cv2
from pyzbar.pyzbar import decode
from threading import Thread
from time import sleep

def chg_time():
    time['text'] = datetime.now().strftime(time_pattern)
    time.after(1000, chg_time)

def chg_tree_content():
    children = product_tree.get_children()
    total_cost = 0
    for child in children:
        product_tree.delete(child)
    for product in products:
        total_cost += products[product]['cost']
        product_tree.insert('', 'end', values=[products[product]['name'],
                                               product,
                                               products[product]['count'],
                                               str(products[product]['price']),
                                               str(products[product]['cost'])])
    lbl_tot['text'] = 'Grand Total: ' + str(total_cost)

def clear_products():
    products.clear()
    chg_tree_content()

def read_code():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(3, 1024)
    camera.set(4, 576)
    keyboard.remove_hotkey("ctrl")
    while keyboard.is_pressed("ctrl"):
        success, frame = camera.read()
        decoded_frames = decode(frame)

        if len(decoded_frames) > 0:
            data = decoded_frames[0].data.decode('utf-8')
            Thread(target=add_product, args=(data,)).start()
            sleep(2)
            chg_tree_content()

        cv2.imshow("Camera", frame)
        cv2.waitKey(1)
    else:
        keyboard.add_hotkey("ctrl", read_code)
        camera.release()
        cv2.destroyAllWindows()

def manual_add():
    def add():
        conn = sqlite3.connect("store.sqlite")
        cur = conn.cursor()
        cur.execute('create table if not exists products'
                    '(name text not null,'
                    'no integer not null primary key,'
                    'price text)')
        product_no = entry_prod_no.get()
        name = entry_product.get()
        count = int(entry_quantity.get())
        price = round(float(entry_price.get()), 2)
        cost = round(count * price, 2)
        cur.execute('insert or replace into products values (?, ?, ?)', (name, int(product_no), str(price)))
        conn.commit()
        product_info = products.get(product_no, dict())
        product_info['name'] = name
        product_info['count'] = count
        product_info['price'] = price
        product_info['cost'] = cost
        products[product_no] = product_info
        chg_tree_content()
        win.destroy()

    win = Toplevel(root)
    win.geometry("540x380+300+50")

    manual_data_frame = Frame(win)
    manual_data_frame.pack(padx=20, pady=10)

    lbl_prod_no = Label(manual_data_frame, text="Prod No.:", font=("calibri", 10))
    lbl_prod_no.grid(row=0, column=0, padx=10, pady=5, sticky="e")

    entry_prod_no = ttk.Combobox(manual_data_frame, font=("arial", 10), values=list(products.keys()))
    entry_prod_no.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    lbl_product = Label(manual_data_frame, text="Product:", font=("calibri", 10))
    lbl_product.grid(row=1, column=0, padx=10, pady=5, sticky="e")

    entry_product = Entry(manual_data_frame, font=("arial", 10), width=40)
    entry_product.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    lbl_quantity = Label(manual_data_frame, text="Quantity:", font=("calibri", 10))
    lbl_quantity.grid(row=2, column=0, padx=10, pady=5, sticky="e")

    entry_quantity = Entry(manual_data_frame, font=("arial", 10), width=10)
    entry_quantity.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    lbl_price = Label(manual_data_frame, text="Price:", font=("calibri", 10))
    lbl_price.grid(row=3, column=0, padx=10, pady=5, sticky="e")

    entry_price = Entry(manual_data_frame, font=("arial", 10), width=10)
    entry_price.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    manual_btn_frame = Frame(win)
    manual_btn_frame.pack(side=BOTTOM, pady=10)

    btn_submit = Button(manual_btn_frame, text="Add", font=("calibri", 10, "bold"), width=10, command=add)
    btn_submit.grid(row=0, column=0, padx=5)

    win.mainloop()

root = Tk()
root.title("Billing System")
root.geometry("1024x650+100+30")

# Variables
time_pattern = "%I:%M:%S %p %a, %b %d, %Y"

h1 = Label(root, text="Billing System", font=("arial", 20, "bold"))
h1.pack(pady=20)

time = Label(root, text=datetime.now().strftime(time_pattern), font=("calibri", 13, "bold"))
time.pack()
chg_time()

data_frame = Frame(root)
data_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

product_tree = ttk.Treeview(data_frame, columns=(1, 2, 3, 4, 5), show='headings')
y_scroll = ttk.Scrollbar(data_frame, orient='vertical', command=product_tree.yview)
product_tree.configure(yscroll=y_scroll.set)

product_tree.pack(side=LEFT, fill=BOTH, expand=True)
y_scroll.pack(side=RIGHT, fill=Y)

product_tree.heading(1, text="Product")
product_tree.column("1", width=400, anchor=CENTER)
product_tree.heading(2, text="Prod No")
product_tree.column("2", width=50, anchor=CENTER)
product_tree.heading(3, text="Quantity")
product_tree.column("3", width=5, anchor=CENTER)
product_tree.heading(4, text="Price ₹")
product_tree.column("4", width=10, anchor=CENTER)
product_tree.heading(5, text="Cost ₹")
product_tree.column("5", width=10, anchor=CENTER)

total_frame = Frame(root)
total_frame.pack(fill=X)

lbl_tot = Label(total_frame, text="Grand Total: 0")
lbl_tot.grid(row=0, column=0, padx=20, pady=5)

btn_frame = Frame(root)
btn_frame.pack(side=BOTTOM, pady=10)

btn_clear = Button(btn_frame, text="Clear", font=("calibri", 10, "bold"), width=10, command=clear_products)
btn_clear.grid(row=0, column=0, padx=5)

btn_add = Button(btn_frame, text="Add", font=("calibri", 10, "bold"), width=10, command=manual_add)
btn_add.grid(row=0, column=1, padx=5)

keyboard.add_hotkey("ctrl", read_code)
root.mainloop()
