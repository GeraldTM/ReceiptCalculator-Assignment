# (c) Gerald_TM 2023
# This is a program that allows you to create a receipt for a customer
# it was made for a school assignment
# 2/17/2023

import configparser, tkinter as tk, mdutils, base64, datetime
from tkinter import Variable, ttk, messagebox

# init config
config = configparser.ConfigParser()
config.read('conf.ini')

# 

# init tkinter
app = tk.Tk()
app.title("Sales Calculator")
app.geometry("650x310")
app.wm_resizable(False, False)
# Set up the variables
receiptVar = Variable()
rawReceipt = list()
costList = list()
productList = list()

# Set up the frames
frame = ttk.Frame(app, padding = "3 3 12 12")

productFrame = ttk.Frame(frame,padding = "3 3 3 3",border=5,relief="solid",width=290,height=480)
productsCanvas = tk.Canvas(productFrame)
productScroll = ttk.Scrollbar(productFrame, orient=tk.VERTICAL, command=productsCanvas.yview)
productsFrame = ttk.Frame(productsCanvas)
searchButton = ttk.Button(productFrame,text="Search",width=7)
productSearchBar = ttk.Entry(productFrame,width=44)

receiptFrame = ttk.Frame(frame, padding = "3 3 3 3")
nameInput = ttk.Entry(receiptFrame, width=40)
receiptList = tk.Listbox(receiptFrame, width=40, height=15, listvariable=receiptVar)
receiptReset = ttk.Button(receiptFrame, text="Reset")
receiptPrint = ttk.Button(receiptFrame, text="Print receipt")

# Funtion for creating a new product frame in the scrollable frame
def productBar(product, useFrame):
    thisProduct = ttk.Frame( useFrame, padding = "3 3 3 3", border=5, relief="solid")

    ttk.Label(thisProduct,text=product[0],width=20).grid(column=0, row=0, sticky=(tk.N))

    ttk.Label( thisProduct, text=product[1], width=20).grid(column=1, row=0, sticky=(tk.N))

    ttk.Label( thisProduct, text=product[2], width=5).grid(column=2, row=0, sticky=(tk.N))

    thisProductQuantity = ttk.Entry( thisProduct, width=5)
    thisProductQuantity.bind("<Return>", lambda e: addProduct(product, int(thisProductQuantity.get())))
    thisProductQuantity.grid(column=2, row=0, sticky=(tk.E))

    thisProductAdd = ttk.Button( thisProduct, text="Add", width=5)
    thisProductAdd.grid(column=3, row=0, sticky=(tk.E))
    thisProductAdd.bind("<Button-1>", lambda e: addProduct(product, int(thisProductQuantity.get())))
    return thisProduct

def searchProduct(value):
    canvasY = ((productsFrame.winfo_height()) / len(productList))
    for product in productList:
        if value.lower() in product[0].lower():
            productSearchBar.delete(0, tk.END)
            productsCanvas.yview_moveto(int(productList.index(product) * canvasY)/1000 - 0.01)
            print((productList.index(product) * canvasY)/1000, 'test', value, product[0], canvasY, productList.index(product))
            return
    productSearchBar.delete(0, tk.END)
    productSearchBar.insert(0, "Product Not Found")
    productSearchBar.select_range(0, tk.END)

def addProduct(product,quantity):
    if quantity > int(product[2]):
        messagebox.showerror("Error", "Not enough stock")
        return
    for item in rawReceipt:
        if item[0] == product[0]:
            if item[1] + quantity > 0:
                item[1] += quantity
                item[2] = item[2]+ (item[1] *float(product[1]))
                receiptList.delete(rawReceipt.index(item)+1)
                costList.append(quantity * float(product[1]))
                receiptList.insert(rawReceipt.index(item)+1, product[0] + " x" + str(item[1]) + ": $" + str(item[1] * float(product[1])))
                receiptList.delete(len(rawReceipt)+1)
                receiptList.insert(len(rawReceipt)+1, "Subtotal: $" + str(round(sum(costList), 2)))
                item[3] = int(product[2]) - int(quantity)
                return
            elif item[1] + quantity == 0:
                item[1] += quantity
                receiptList.delete(rawReceipt.index(item)+1)
                rawReceipt.remove(item)
                return
            else:
                messagebox.showerror("Error", "Quantity must not be negative")
                return
    if quantity > 0:
        rawReceipt.append([product[0],quantity,quantity*float(product[1])])
        costList.append(quantity * float(product[1]))
        receiptList.insert((len(rawReceipt)) ,product[0] + " x" + str(quantity) + ": $" + str(quantity * float(product[1])))
        receiptList.delete(len(rawReceipt)+ 1)
        receiptList.insert((len(rawReceipt)+ 1) ,"Subtotal: $" + str(round(sum(costList), 2)))
        product[2] = int(product[2]) - int(quantity)
    else:
        messagebox.showerror("Error", "Quantity must be greater than 0")
        return

def printReceipt():
    config["Meta"]["totalsales"] = str(int(config["Meta"]["totalsales"]) + 1)
    receipt = mdutils.MdUtils(file_name='sale' + str(config["Meta"]["totalsales"]), title='Receipt')
    receipt.new_line(nameInput.get())
    receipt.new_line(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    receipt.new_line('')
    receipt.new_line('items purchased:')
    for item in rawReceipt:
        receipt.new_line(item[0] + " x" + str(item[1]) + ": $" + str(round(float(item[2]), 2)))
    receipt.new_line('Subtotal: $' + str(round(sum(costList), 2)))
    receipt.new_line('Tax: $' + str(round(sum(costList) * 0.13, 2)))
    receipt.new_line('Total: $' + str(round(sum(costList) * 1.13, 2)))
    receipt.create_md_file()
    receipt.new_line('')
    receiptList.delete(1, tk.END)
    rawReceipt.clear()
    costList.clear()

# get list of products from conf.ini
for key in config['Products']:
    productValues = config.get('Products',key).split(',')
    key = key.replace('_',' ')
    productValues.insert(0,key)
    productList.append(productValues)

# Set initial values
productSearchBar.insert(0, "Search Products...")
receiptList.insert(0, "Products")

nameInput.insert(0, "Name: ")

# GUI Funtionality setup
productsFrame.bind("<Configure>", lambda e: productsCanvas.configure(scrollregion=productsCanvas.bbox("all")))
productsCanvas.create_window((0,0), window=productsFrame, anchor="nw")
productsCanvas.configure(yscrollcommand=productScroll.set)

searchButton.bind("<Button-1>", lambda e:searchProduct(productSearchBar.get()))

productSearchBar.bind("<Button-1>", lambda e: productSearchBar.delete(0, tk.END) if productSearchBar.get() == "Search Products..." or productSearchBar.get() == "Product Not Found" else productSearchBar.select_range(0, tk.END))
productSearchBar.bind("<Return>", lambda e: searchProduct(productSearchBar.get()))

receiptReset.bind("<Button-1>", lambda e: (receiptList.delete(1, tk.END), rawReceipt.clear(), costList.clear()))
nameInput.bind("<Button-1>", lambda e: nameInput.delete(0, tk.END) if nameInput.get() == 'Name: ' else nameInput.select_range(0, tk.END))
receiptPrint.bind("<Button-1>", lambda e: (printReceipt()))

for product in productList:
    productBar(product, useFrame=productsFrame).grid(column=0, row=productList.index(product)+2, sticky=('nw'))

# GUI Layout setup
productScroll.grid(column = 0, row = 1, sticky = 'ens')
productsCanvas.grid(column=0, row=1, sticky=("nws"))

searchButton.grid(column=0, row=0, sticky=(tk.E))
productSearchBar.grid(column=0, row=0, sticky=(tk.W))
productFrame.grid(column=1, row=0, sticky=('nes'))

receiptList.grid(column=0, row=1, sticky=(tk.N))
nameInput.grid(column=0, row=0, sticky=(tk.N))
receiptReset.grid(column=0, row=2, sticky=(tk.W))
receiptPrint.grid(column=0, row=2, sticky=(tk.E))
receiptFrame.grid(column=0, row=0, sticky=(tk.W))

frame.grid(column=0,row=0,sticky=('nesw'))

# App loop
app.mainloop()
running = True
while running:
    try:
        app.winfo_exists()
    except:
        running = False
        break
    app.update()
    app.update_idletasks()

#update stock
for item in rawReceipt:
    config.set('Products', item[0].replace(' ','_'), (str(item[1])+","+str(item[3])))

# Write to config file
with open ('conf.ini', 'w') as configfile:
    config.write(configfile)