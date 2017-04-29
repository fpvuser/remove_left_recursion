import numpy as np
import pandas as pd
import re
import itertools
from error import *

class Term:
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return str(self.name)
    
    def __repr__(self):
        return str(self.name)
    
    def __eq__(self, other): 
        return self.name == other.name
    
    def __hash__(self):
        return hash(str(self))

class NoTerm:
    def __init__(self, name):
        self.name = name
        
    def __str__(self):
        return str(self.name)
    
    def __repr__(self):
        return str(self.name)
    
    def __eq__(self, other): 
        return self.name == other.name
    
    def __hash__(self):
        return hash(str(self))
    
class Grammar:
    eps = 'Epsilon'
    def __init__(self, terms, no_terms):
        self.terms = set(terms)
        self.no_terms = set(no_terms)
        self.productions = []
        self.start = None
        
    def get_no_terms(self):
        return self.no_terms
    
    def get_terms(self):
        return self.terms - set([Term(Grammar.eps)])
        
    def add_no_term(self, no_term):
        self.no_terms.add(no_term)
        
    def add_no_terms(self, no_terms):
        self.no_terms |= set(no_terms)
        
    def remove_no_term(self, remove_term):
        self.no_terms.remove(remove_term)
        
    def remove_no_terms(self, remove_set):
        self.no_terms -= set(remove_set)
        
    def get_start(self):
        return self.start
        
    def __str__(self):
        prods_str = '\n'
        for prod in self.productions:
            prods_str += str(prod)+'\n'
        prods_str += '-----------'
        return '-----------\n'+str(self.terms - set([Term(Grammar.eps)]))+'\n'+str(self.no_terms)+'\n'+prods_str
    
    def __repr__(self):
        prods_str = '\n'
        for prod in self.productions:
            prods_str += str(prod)+'\n'
        prods_str += '-----------'
        return '-----------\n'+str(self.terms - set([Term(Grammar.eps)]))+'\n'+str(self.no_terms)+'\n'+prods_str
        
    def get_no_term_number(self, no_term):
        if no_term not in self.no_terms:
            raise ValueError
        for i, prod in enumerate(self.productions):
            if no_term == prod[0]:
                return i
        raise ProductionSearchError
        
    def add_production(self, production):
        if production[0] not in self.no_terms:
            raise GrammarError
        else:
            try:
                i = self.get_no_term_number(production[0])
                self.productions[i][1].extend(production[1])
            except ProductionSearchError:
                self.productions.append(production)
        if len(self.productions) == 1:
            self.start = self.productions[0][0]
            
    def add_production_to_head(self, production):
        if production[0] not in self.no_terms:
            raise GrammarError
        else:
            try:
                i = self.get_no_term_number(production[0])
                raise GrammarError
                #self.productions[i][1].extend(production[1])
            except ProductionSearchError:
                self.productions.insert(0, production)
                self.start = self.productions[0][0]
            
                
    def to_no_left_recursion(self):
        new_gram = Grammar(self.terms, self.no_terms)
        for i, prod_line in enumerate(self.productions):
            curr_no_term = prod_line[0]
            new_prod_line = [curr_no_term, []]
            for prod in prod_line[1]:
                if isinstance(prod[0], Term) or self.get_no_term_number(prod[0]) >= i:
                    new_prod_line[1].append(prod)
                else:
                    j = self.get_no_term_number(prod[0])
                    for jprod in self.productions[j][1]:
                        new_prod = jprod
                        new_prod_line[1].append(new_prod + prod[1:])
            new_prod_lines, new_no_terms = get_no_direct_left_recursion(new_prod_line)
            new_gram.add_no_terms(new_no_terms)
            for line in new_prod_lines:
                new_gram.add_production(line)
        return new_gram
    
    def _get_eps_no_terms(self):
        eps_no_terms = set()
        for i, prod_line in enumerate(self.productions):
            curr_no_term = prod_line[0]
            for prod in prod_line[1]:
                if prod[0] == NoTerm(Grammar.eps):
                    eps_no_terms.add(curr_no_term)
                    break
        pre_eps_no_terms = set()
        while pre_eps_no_terms != eps_no_terms:
            pre_eps_no_terms = set(list(eps_no_terms))
            for i, prod_line in enumerate(self.productions):
                if prod_line[0] in eps_no_terms:
                    continue
                curr_no_term = prod_line[0]
                flag = True
                for prod in prod_line[1]:
                    for a in prod:
                        if a not in eps_no_terms:
                            flag = False
                            break
                    if flag:
                        eps_no_terms.add(curr_no_term)
                        break
        return eps_no_terms
    
    def remove_eps(self):
        if len(self.productions) == 0:
            return self
        eps_no_terms = self._get_eps_no_terms()
        no_eps_gram = Grammar(self.terms, self.no_terms)
        
        for i, prod_line in enumerate(self.productions):
            #no_eps_gram.add_production(prod_line[:])
            curr_no_term = prod_line[0]
            new_prod_line = [curr_no_term, []]
            for prod in prod_line[1]:
                new_prod_line[1] += (_build_prod_combinations(prod[:], eps_no_terms))
            no_eps_gram.add_production(new_prod_line)
        no_eps_gram._remove_eps()
        
        if self.get_start() in eps_no_terms:
            new_start = NoTerm(self.get_start().name+'\'')
            start = NoTerm(self.get_start().name)
            no_eps_gram.add_no_term(new_start)
            start_prod = [new_start, [[start], [NoTerm(Grammar.eps)]]]
            no_eps_gram.add_production_to_head(start_prod)
            
        return no_eps_gram
    
    def _remove_eps(self):
        for i, prod_line in enumerate(self.productions):
            for j, prod in enumerate(prod_line[1]):
                if prod[0] == NoTerm(Grammar.eps):
                    del prod_line[1][j]
            if len(prod_line[1]) == 0:
                self.remove_no_term(prod_line[0])
                del self.productions[i]
                
    def to_string(self, with_terms=False):
        str_grammar = ''
        if with_terms:
            str_grammar += str(self.get_no_terms()) + '\n'
            str_grammar += str(self.get_terms()) + '\n\n'
        for i, prod_line in enumerate(self.productions):
            str_prods = ' | '.join([''.join(map(str, prod)) for prod in prod_line[1]])
            str_grammar += str(prod_line[0]) + ' -> ' + str_prods + '\n'
        return str_grammar
                

def _build_prod_combinations(prod, eps_no_terms):
    eps_set = []  ## Заменить на список! Переделать комбинацию ABA -> 123 и переставлять числа!
    temp_prod = []
    for a in prod:
        if a in eps_no_terms:
            eps_set.append(a)
            temp_prod.append(len(eps_set)-1)
        else:
            temp_prod.append(a)
    #return [prod]
            
    if len(eps_set) == 0:
        return [prod]
    
    comb = []
    for i in range(len(eps_set)+1):
        i_comb = itertools.combinations(range(len(eps_set)), i)
        for c in i_comb:
            curr_comb = []
            for a in temp_prod:
                #print('a: ',a, 'eps_set: ', eps_set, 'comb: ', c)
                if (isinstance(a, int)) and (a in c):
                    curr_comb.append(eps_set[a])
                elif (not isinstance(a, int)):
                    curr_comb.append(a)
            if len(curr_comb) != 0:
                comb.append(curr_comb)
    return comb
            
def get_no_direct_left_recursion(prod_line):
    flag = False
    res = []
    bprod = []
    aprod = []
    new_no_terms = []
    for prod in prod_line[1]:
        if prod[0] == prod_line[0]:
            aprod.append(prod[1:])
        else:
            bprod.append(prod[:])
    if len(aprod) == 0:
        res.append(prod_line)
    else:
        new_no_term = NoTerm(prod_line[0].name+'\'')
        new_no_terms.append(new_no_term)
        b_line = [prod_line[0], []]
        for prod in bprod:
            b_line[1].append(prod+[new_no_term])
        a_line = [new_no_term, []]
        for prod in aprod:
            a_line[1].append(prod+[new_no_term])
        a_line[1].append([NoTerm(Grammar.eps)])
        res.append(b_line)
        res.append(a_line)
    return res, new_no_terms
        
        
def split_to_terms(str_terms, str_no_terms, string):
    r_terms = []
    for t in str_terms:
        r_terms.append(re.escape(t))
    r_no_terms = []
    for t in str_no_terms:
        r_no_terms.append(re.escape(t))
    str_prods = string.split('->')
    prod_by_terms = []
    
    prod_by_terms.append(str_to_terms(str_terms, str_no_terms, [str_prods[0].strip()])[0])
    for str_prod in str_prods[1].split('|'):
        str_list = [i for i in re.findall('|'.join(r_no_terms)+'|'+'|'.join(r_terms), str_prod) if i]
        prod_by_terms.append(str_to_terms(str_terms, str_no_terms, str_list))
    str_list = [i for i in re.findall('|'.join(r_no_terms)+'|'+'|'.join(r_terms), string) if i]
    return prod_by_terms
    #return str_to_terms(str_terms, str_no_terms, str_list)

def str_to_terms(str_terms, str_no_terms, str_list):
    term_list = []
    for term in str_list:
        if term in str_terms:
            term_list.append(Term(term))
        elif term in str_no_terms:
            term_list.append(NoTerm(term))
        else:
            print('Error with: '+term)
            raise TermError
    return term_list

def to_production(terms_list):
    return [terms_list[0], terms_list[1:]]

def string_to_grammar(gram_str):
    str_no_terms = gram_str[1].split(' ')
    str_terms = gram_str[3].split(' ')
    str_terms.append(Grammar.eps)
    
    no_terms = str_to_terms(str_terms, str_no_terms, str_no_terms)
    terms = str_to_terms(str_terms, str_no_terms, str_terms)

    gram = Grammar(terms, no_terms)
    for line in gram_str[5:]:
        production = to_production(split_to_terms(str_terms, str_no_terms, line))
        #print(production)
        gram.add_production(production)
        
    return gram

def string_to_grammar_par(gram_str):
    str_no_terms = re.findall('<\S+>|<\S+.*?\S+>|\S+', gram_str[1])
    str_terms = re.findall('<\S+>|<\S+.*?\S+>|\S+', gram_str[3])
    str_terms.append(Grammar.eps)
    
    no_terms = str_to_terms(str_terms, str_no_terms, str_no_terms)
    terms = str_to_terms(str_terms, str_no_terms, str_terms)

    gram = Grammar(terms, no_terms)
    for line in gram_str[5:]:
        production = to_production(split_to_terms(str_terms, str_no_terms, line))
        #print(production)
        gram.add_production(production)
        
    return gram

def file_to_grammar(filename):
    input_file = open(filename, 'r')
    input_gram_str = []
    for line in input_file:
        input_gram_str.append(line.strip())
    input_file.close()
    return string_to_grammar(input_gram_str)

def file_to_grammar_par(filename):
    input_file = open(filename, 'r')
    input_gram_str = []
    for line in input_file:
        input_gram_str.append(line.strip())
    input_file.close()
    return string_to_grammar_par(input_gram_str)