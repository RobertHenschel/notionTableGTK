#!/usr/bin/env python3

# URL: https://python-gtk-3-tutorial.readthedocs.io/en/latest/treeview.html
# URL: https://github.com/jamalex/notion-py

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from notion.client import NotionClient
import threading

# Global variables
config  = {}
client  = 0

# Login to Notion.so
def loginNotion():
    # Obtain the `token_v2` value by inspecting your browser cookies on a logged-in session on Notion.so
    # In the Chrome browser, go to Settings -> Privacy and security -> Site Settings -> Cookies and site data -> See all cookies and site data -> www.notion.so -> toek_v2 -> Content 
    global client
    client = NotionClient(token_v2=config["token_v2"])
    return

# Retrieve Items from Notion
def getItems(listStore, busyIndicator):
    # Login to notion
    loginNotion()
    
    # Get all rows in the collection
    cv = client.get_collection_view(config["collectionID"])
    rows = cv.default_query().execute()

    # Loop through rows and insert them into a the listStore for the treeView
    for row in rows:
        listElement = []
        # Retrieve the value of each property and store in a list
        # Yes, order matters here!
        listElement.append(str(row.name))
        listElement.append(str(row.tags))
        try:
            # if priority is not set in notion, it will return "none", which will fail 
            # the convertion to an int
            listElement.append(int(row.priority))
        except:
            listElement.append(int())
        try:
            # same as for priority above... if there is no due date, then there is no property
            # "start" causing an exception
            listElement.append(str(row.due_date.start))
        except:
            listElement.append(str(""))
        listElement.append(str(row.status))
        # now put all items into the listStore
        listStore.append(list(listElement))

    # reset the busy indicator
    busyIndicator.set_from_file("light_off.png")
    return

def addItem(item, busyIndicator):
    # create a new row in the collection
    collectionID = config["collectionID"]
    cv = client.get_collection_view(collectionID)
    row = cv.collection.add_row()
    # when setting the properties of the row, API calls to Notion are done in the background,
    # so this could take a while
    row.name = item[0]
    row.tags = item[1]    
    row.priority = item[2]
    row.due_date = item[3]
    row.status = item[4]
    # reset the busy indicator
    busyIndicator.set_from_file("light_off.png")
    return

def deleteItem(text,busyIndicator):
    collectionID = config["collectionID"]
    cv = client.get_collection_view(collectionID)
    rows = cv.default_query().execute()
    # Loop through rows
    for row in rows:
        # if the "name" matches, delete the row
        if str(row.name) == text:
            row.remove()
            break
    # reset the busy indicator
    busyIndicator.set_from_file("light_off.png")
    return

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="ToDo Items")
        
        self.resize(800,100)
        # Entry field at the top of the window
        self.entry = Gtk.Entry()
        self.entry.connect("key-release-event", self.on_key_release)
        # Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # the busy indicator
        self.busyIndicator = Gtk.Image.new_from_file('light_on.png')
               
        # Creating the ListStore model with as many "columns" as the collection has properties
        self.listStore = Gtk.ListStore(str,str,int,str,str)
        
        # get all items of the collection from Notion.
        # as this can take a while, lets do that in a separate thread
        threading.Thread(target=getItems, args=(self.listStore,self.busyIndicator,)).start()

        # Creating a treeview widget with the listStore as the source
        self.treeview = Gtk.TreeView.new_with_model(self.listStore)
        # register a listener for mouse events, so a context manue can be shown
        self.treeview.connect('button-press-event', self.contextMenu)

        # Setting column title and renderer
        for i, column_title in enumerate(["Name","Tags","Priority","Due Date","Status"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_resizable(True)
            self.treeview.append_column(column)
        
        # Setting up the layout, putting the treeview in a scrollwindow
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.busyIndicator,7,0,1,1)
        self.grid.attach(self.entry, 0,0,7,1)
        self.grid.attach(self.scrollable_treelist, 0, 1, 8,5)
        
        self.scrollable_treelist.add(self.treeview)
        self.show_all()
        
        self.treeview.get_column(0).set_max_width(500)
        self.treeview.get_column(3).set_max_width(100)

        # prepare context menu
        self.cmenu = Gtk.Menu.new()
        self.cm_item = Gtk.MenuItem.new_with_label('Delete')
        # connect the "Delete" menu in the context menu with the self.deleteItem function
        self.cm_item.connect("activate", self.deleteItem)
        self.cmenu.append(self.cm_item)
        self.cmenu.show_all()

    def on_key_release(self, widget, ev):
        # this gets called every time a user releases a key in the entry field
        text = widget.get_text()
        # check if the last key released was "Enter"/"Return"
        if Gdk.keyval_name(ev.keyval) == "Return":
            #if yes, lets setup a new list element, again, order matters!
            listElements = []
            listElements.append(str(text))
            listElements.append(str(""))
            listElements.append(int(3))
            listElements.append(str(""))
            listElements.append(str("Next Action"))
            # put the item into the list store
            self.listStore.append(list(listElements))
            # set the busy indicator
            self.busyIndicator.set_from_file("light_on.png")
            # put the item into the Notion collection
            # since this will make API calls over the network, lets do that in a separate thread
            threading.Thread(target=addItem, args=(listElements,self.busyIndicator,)).start()
            # clear the entry field
            widget.set_text("")
        return
    
    def contextMenu(self, widget, ev):
        # this gets called when the user presses a mouse button in the treeview widget
        # check for the right mouse button
        if ev.button == 3:
            # model is the index into the listStore
            # the following line would output the "name" of the item to delete
            #print(str(self.listStore[model][0]))
            model, path, __, __ = self.treeview.get_path_at_pos(int(ev.x), int(ev.y))
            # show the context menu
            self.cmenu.popup_at_pointer()
            # save the index into the listStore for later when the user hits the "Delete" menu
            self.rowToDelete = model
        return
    
    def deleteItem(self, w):
        text = str(self.listStore[self.rowToDelete][0])
        # check for duplicate rows (this is a hack, it would be better to find a unique ID
        # rather than going by the "name" of the item in the row)
        count = 0
        for item in self.listStore:
            if item[0] == text:
                count = count + 1
        if count != 1:
            # and here is the result of the hack from above... if there are two items in the 
            # list with the same name... the delete action will fail... just to be save and not
            # delete the wrong item by accident
            print("Error: found more than one list item with the same name. Aborting Delete.")
            print("   Item to delete was: "+text)
            return
        # deleting is a two step process... first delete the item from the listStore
        for item in self.listStore:
            if item[0] == text:
                self.listStore.remove(item.iter)
                break
        # set the busy indicator
        self.busyIndicator.set_from_file("light_on.png")
        # now delete the item from the Notion collection via API calls
        threading.Thread(target=deleteItem, args=(text,self.busyIndicator,)).start()
        return

# Read config from file
with open("config.dat") as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        config[name.strip()] = str(var).strip()

# Create window
win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()