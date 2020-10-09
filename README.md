# notionTableGTK
The purpose of this project is to connect to [Notion.so](https://www.notion.so) from a python application, retrieve the content of a collection and display it in a GTK+ 3 Treeview widget. This project relies heavily on [notion-py](https://github.com/jamalex/notion-py) to connect and download data from Notion.so and [Treeview example code](https://python-gtk-3-tutorial.readthedocs.io/en/latest/treeview.html) of the Python GTK+ 3 Tutorial.

## Disclaimer

This is my first attempt at building a GTK+ application and I don't claim that I have followed best practices for any of my code. If you have suggestions for improvements, please open an issue or create a pull request.
This code is mostly intended as a starting point and can be extended in various ways. There should be enough code here to give you an idea of how to get the data and display it.

## Installation and Configuration

Before running the application, you need to make 2 changes to *config.dat*. Those changes are different for every user, so no default values are provided.

The first entry that needs to be set in *config.dat* is *token_v2*, which is the access token to your Notion account. You can find that token by looking at cookies that the notion website stores in your browser. The value you are looking for is called *token_v2* and it is stored in a cookie for *www.notion.so*. You are looking for a value that is 150 or more characters long and contains letters and digits.

The other entry in *config.dat* is *collectionID*, which is the URL to the collection/table in Notion. You can retrieve this by navigating to the collection in your browser and then open the *menu* for the collection and copy the link. What you are looking for is the link to the collection, not the link to the page that contains the collection! Here is a picture that may help point you in the right direction. ![](./img/notionCollectionLink.jpg)

*config.dat* should look something like this, just with way longer lines:

```
token_v2 = 62acf60905ad9f28df60905ad9f28...
collectionID = https://www.notion.so/82f1240e0f89...
```
Once *config.dat* is updated you should be good to run the application.

## Features and Limitations

This application should work for arbitrary collection in Notion, but was only tested on a few examples. All property types of a Notion collection are converted to a *string* in python, which may not be optimal for displaying them. Customization to the view of a collection are not preserved, meaning filters and custom sort orders are be ignored. Both features could be implemented through the notion-py API or in the tree view list store. The application has only been tested on Linux.

## Example Output

Here is a screen shot of what a collection in Notion looks like, and how it is displayed in the GTK+ 3 Treeview widget.

![](./img/NotionCollection.jpg) ![](/home/henschel/Desktop/notionTableGTK/img/GTKApp.jpg)

