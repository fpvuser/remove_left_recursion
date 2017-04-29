import numpy as np
import pandas as pd
import re
import itertools
import error
from grammar import *

def remove_left_recursion(file_name):
    gram = file_to_grammar(file_name)
    print(gram.to_string())
    no_left_gram = gram.to_no_left_recursion()
    #print(no_left_gram.get_no_terms())
    #print(no_left_gram.get_terms(), '\n')
    print(no_left_gram.to_string())
    
def remove_eps(file_name):
    gram = file_to_grammar(file_name)
    print(gram.to_string())
    no_eps_gram = gram.remove_eps()
    print(no_eps_gram.to_string())

remove_left_recursion('input.txt')