# Copyright (c) 2014 Grameen Foundation
from motech import execute_javasphinx

def setup(app):
    app.connect('builder-inited', execute_javasphinx)
