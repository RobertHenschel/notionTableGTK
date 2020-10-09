#!/usr/bin/env python3

# URL: https://python-gtk-3-tutorial.readthedocs.io/en/latest/treeview.html
# URL: https://github.com/jamalex/notion-py

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from notion.client import NotionClient

# Global variables
config  = {}
client  = 0
properties = []

# Login to Notion.so
def loginNotion(token):
    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
    # In the Chrome browser, go to Settings -> Privacy and security -> Site Settings -> Cookies and site data -> See all cookies and site data -> www.notion.so -> toek_v2 -> Content 
    client = NotionClient(token_v2=token)
    return(client)

# Retrieve Items from Notion
def getItems(client, collectionID):
    # Get all rows in the collection
    cv = client.get_collection_view(collectionID)
    rows = cv.default_query().execute()
    
    # Get the properties (columns) of the collection
    row = rows[0]
    for j in range(0,len(row.schema)):
        properties.append(row.schema[j]['slug'])

    # Get the content for all rows
    itemList = []
    for row in rows:
        listElements = []
        # Retrieve the value of each property
        for count in range(0, len(properties)):
            listElements.append(str(getattr(row,properties[count])))
        # This will go into the list store later, so it has to be a list of lists
        itemList.append(list(listElements))
    
    return itemList

class MyWindow(Gtk.Window):
    def __init__(self, items):
        Gtk.Window.__init__(self, title="Notion Collection in GTK+ 3")
        
        self.resize(500,200)
        # Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # Creating the ListStore model with as many "columns" as the collection has properties
        self.listStore = Gtk.ListStore(*([str]*len(properties)))
        
        # Adding all rows from the collection into the listStore
        for item in itemList:
            self.listStore.append(item)

        # Creating a treeview widget with the listStore as the source
        self.treeview = Gtk.TreeView.new_with_model(self.listStore)

        # Setting column title and renderer
        for i, column_title in enumerate(properties):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)
        
        # Setting up the layout, putting the treeview in a scrollwindow
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        
        self.scrollable_treelist.add(self.treeview)
        self.show_all()

# Read config from file
with open("config.dat") as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        config[name.strip()] = str(var).strip()

# Login to notion
client = loginNotion(config["token_v2"])

# Retrieve items from table
itemList =  getItems(client, config["collectionID"])

# Create window
win = MyWindow(itemList)
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()