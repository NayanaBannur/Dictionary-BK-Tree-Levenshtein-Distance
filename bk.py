#Import modules

import dict
import time
import os
import sys

try:
    # Python 2
    from future_builtins import filter
except ImportError:
    # Python 3
    pass
    
try:
    #Python 2
    from itertools import imap,izip
except ImportError:
    # Python 3
    imap=map
    izip=zip
    
#Program     

class BKTree:
    def __init__(self, distancefunction,words,definitions):
        
        '''
        Creates a BK-tree using Levenshtein distance and the given word and definition lists.
        Parameters:
        distancefunction: Returns the Levenshtein distance between two words
        words: An iterable which produces words that can be passed to the distance function
        '''
        
        self.distancefunction = distancefunction
        
        #Declare iterators it over the given list of words and definitions
        it_word = iter(words)
        it_def = iter(definitions)
        root_word = next(it_word)
        root_def = next(it_def)
        
        #Initialize the tree to root and empty dictionary representing children
        self.tree = (root_word, root_def, {})
        
        #Call add_word for each word in the list to create the tree
        for i,j in izip(it_word,it_def):
            #node = Node()
            self.add_word(self.tree,i,j)

    def add_word(self, parent, word, definition):
        parent_word,_,children = parent #Parent associated with a word, definition and a list of children
        
        #Calculate the distance of the given word from the parent word
        d = self.distancefunction(word, parent_word)
        
        #If there is a child node of the calculated distance, then recursively call add_word for that subtree. Otherwise add a new child node to the parent node.
        if d in children:
            self.add_word(children[d], word, definition)
        else:
            children[d] = (word, definition, {})

    def query_util(self,parent,word,n):
        
        parent_word,definition,children = parent
        
        #Calculate the distance of the given word from the parent word
        d = self.distancefunction(word, parent_word)
        
        results = []
        
        #If distance is less than n, add the word to the results
        if d <= n:
            results.append((d, parent_word,definition))
        
        #Recursively iterate over subtrees    
        for i in range(d-n, d+n+1): #from d-n to d+n

            child = children.get(i)
            
            #If the child exists, extend the list 'results' with the words found in the child subtrees
            if child is not None:
               results.extend(self.query_util(child,word,n))
                
        return results
    
    def query(self, word, n):
        
        '''
        This function returns the words in the tree which are at a distance <=n from the given word.  
        Parameters:
        word: The word to be queried for
        n: A non-negative integer that specifies the allowed distance from the query word.  
        It return a list of tuples (distance, word, definition) sorted in ascending order of distance.
        '''

        # sort by distance
        return sorted(self.query_util(self.tree,word,n))
       
        
def brute_query(word, words, distancefunction, n):
    
    '''
    This function is a brute force distance query, for the purpose of evaluating performance.
    Parameters:
    word: the word to be queried for
    words: An iterable which produces words
    distancefunction: Returns the Levenshtein distance between 'word' and another word in 'words'
    n: A non-negative integer that specifies the allowed distance from the query word
    '''
    
    return [i for i in words
            if distancefunction(i, word) <= n]

def levenshtein(string1, string2):
    
    #Iterative with full matrix implementation
    #Based on Wagner-Fischer Algorithm
    
    m, n = len(string1), len(string2)
    d = [range(n+1)] # d is a list from 0 to n(inclusive)
    d += [[i] for i in range(1,m+1)]
    for i in range(0,m):
        for j in range(0,n):
            cost = 1
            if string1[i] == string2[j]: cost = 0

            d[i+1].append( min(d[i][j+1]+1, #deletion
                               d[i+1][j]+1, #insertion
                               d[i][j]+cost) #substitution
                           )
    return d[m][n]

def timeof(fn, *args):
   
    start = time.time()
    res = fn(*args)
    end = time.time()
    t = end-start
    return res,t
    
def maxdepth(tree, count=0):
    _,_, children = tree
    if len(children):
        return max(maxdepth(i, count+1) for i in children.values())
    else:
        return count

def insert_word(dict_tree):
   print("Inserting a new word")
   print("Enter the word to be added:")
   wd = str(input())
   
   print("Enter the definition of the word:")
   defn = str(input())
   
   search_res = dict_tree.query(wd, 0)
   if not search_res:
      dict_tree.add_word(dict_tree.tree,wd,defn)
      dict.add_dict(wd,defn)
   else:
      print("This word aleady exists in the dictionary.")
        
def lookup(dict_tree):
   print("Look up a word in the dictionary")
   print("Enter the word to look up")
   wd = str(input())
   
   search_res = dict_tree.query(wd, 0)
   
   if not search_res:
      print("No match found!")
      
   else:
      print(search_res[0][1]+" : "+search_res[0][2])

def spellcheck(dict_tree):
   print("Spell Check")
   print("Enter the word")
   wd = str(input())
   
   distance = 0
   
   search_res = dict_tree.query(wd, distance)
   
   if not search_res:
      while(distance<=2):
      
         if distance==2:
            print("Suitable suggestions were not found")
            break
            
         else:
            distance = distance + 1
            search_res = dict_tree.query(wd, distance)
            
            if not search_res:
               continue
               
            else:
               if len(search_res)==1:
                  print("The correct word is:")
                  print(search_res[0][1])
                  break
               print("No matches found. Did you mean:")
               count = 0
               for res in search_res:
                  if count==10:
                     break
                  print(res[1])
                  count = count + 1 
               break               
         
   else:
  
      print("The spelling is correct! The word entered was:")
      print(search_res[0][1]+" : "+search_res[0][2]) 

def compare_queries(dict_tree,wordlist):
   print("Compare searches by brute query and Levenshtein distance-based query")
   print("Enter the word to look up")
   wd = str(input())
   
   search_res = dict_tree.query(wd, 0)
   
   if not search_res:
      print("No match found!")
      
   else:
      print(search_res[0][1]+" : "+search_res[0][2])
      print("Levenshtein distance-based query:")
      _,t1 = timeof(dict_tree.query,wd,0)
      print("Time taken (in seconds): "+str(t1))
      print("Brute query:")
      _,t2 = timeof(brute_query,wd,filter(len,wordlist),levenshtein,0)
      print("Time taken (in seconds): "+str(t2))

def sentence_correct(dict_tree):
    print("Spell check tool for sentences")
    other_words = []
    print("Enter a sentence")
    sent = str(input())
    words = sent.split()
    print("The sentence has been corrected to:")
    for wd in words:
       word = wd
       if '.' in wd or '?' in wd or ',' in wd or '!' in wd:
          word = wd[:-1]
       if (wd and wd[0].isupper()):
          word = word[0].lower() + word[1:]
       search_res = dict_tree.query(word, 0)
       if not search_res:
          search_res = dict_tree.query(word, 1)
          if len(search_res)==1:
             if (wd and wd[0].isupper()):
                search_res[0][1][0].upper()
             if '.' in wd:
                print(search_res[0][1]+".",end=" ")
             elif ',' in wd:
                print(search_res[0][1]+",",end=" ")
             elif '?' in wd:
                print(search_res[0][1]+"?",end=" ")
             elif '!' in wd:
                print(search_res[0][1]+"!",end=" ")
             else:
                print(search_res[0][1],end=" ")
          else:
             print(wd,end=" ")
             other_words.append(word)
       else:
          print(wd,end=" ")
    print("\n")
    
    if not other_words:
       return None
    else:
       print("Some words could not be autocorrected. Suggestions are given below:\n")
    pos = 0
    for wd in list(other_words):
       start = sent.find(wd,pos)
       end = start+len(wd)
       print(sent[0:start],end="")
       print('\033[1m',end="")
       print(wd,end="")
       print('\033[0m',end="")
       print(sent[end:])
       distance = 0
       count = 0
       while(distance<=2):
      
          if distance==2:
             print("Suitable suggestions were not found\n")
             break
            
          else:
             distance = distance + 1
             search_res = dict_tree.query(wd, distance)
            
             if not search_res:
                continue
               
             else:
                print("Did you mean:")
                for res in search_res:
                   if count==10:
                      break
                   print(str(count+1)+". "+res[1])
                   count = count + 1 
                break
       
       print("Press any character to continue")
       c = input()
       pos = pos + len(wd) + 1

if __name__ == "__main__":
   
    wordlist = []
    defintionlist = []
    
    wordlist, definitionlist = dict.load_dict()
    
    print("Creating BK-tree...\n")
    dict_tree,t = timeof(BKTree,levenshtein,filter(len,wordlist),filter(len,definitionlist))
    print("The BK-tree has been created.\n")
    
    while True:

       print("DICTIONARY USING BK-TREES\n")

       print("1: Insert a new word into the dictionary")
       print("2: Look up a word in the dictionary")
       print("3: Check whether the spelling of a given word is correct")
       print("4: Compare searches by brute query and Levenshtein distance-based query")
       print("5: Performance and characteristics")
       print("6: Spell check tool for sentences")
       print("Any other character to exit\n")
       
       try:
          x = int(input())
          
       except:       
          print("Enter a valid choice")
          continue
          
       if x==1:
          insert_word(dict_tree)
          
       elif x==2:
          lookup(dict_tree)
           
       elif x==3:
          spellcheck(dict_tree)
          
       elif x==4:
          compare_queries(dict_tree,wordlist)

       elif x==5:
          print("Size of dictionary: "+str(len(wordlist)))
          print("The depth of the tree is: "+str(maxdepth(dict_tree.tree)))
          print("Time taken to create the tree: "+str(t)+" seconds")
       
       elif x==6:
          sentence_correct(dict_tree)
          
       elif x==7:
          spell_check_tool(dict_tree)
          
       else:
          print("Are you sure you want to exit? (Y/N)")
          c = input()
          os.system('clear||cls')
          if ((c=='Y') or (c=='y')):
             sys.exit(0)
          else:
             continue
       
       print("\nContinue? (Y/N)")
       c = input()
       
       if ((c=='Y') or (c=='y')):
          os.system('clear||cls')
          continue
          
       else:
          print("Are you sure you want to exit? (Y/N)")
          c = input()
          os.system('clear||cls')
          if ((c=='Y') or (c=='y')):
             break
          else:
             continue