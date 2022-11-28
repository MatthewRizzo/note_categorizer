"""This is the server aspect of the web app. It is responsible for managing all
routes and handlers with requests from the client(s)."""
from note_categorizer.categorizer.parser import Parser
from note_categorizer.common.category import Category

valid_category = [Category("foo", ["bar", "fizz"])]
Parser(valid_category)
print("hello world from server")
