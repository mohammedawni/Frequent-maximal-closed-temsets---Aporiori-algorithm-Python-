import sqlite3
from math import factorial
import itertools
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph
#################################################################################
class Item_Sets :
    def __init__(self , db_file_name   ) :
        self.transactions = self.initialize_transactions(db_file_name)
        self.unique_transaction = self.initialize_unique_transaction()

      
    def initialize_transactions(self,db_file_name) :
        conn = sqlite3.connect(db_file_name)
        cur  = conn.cursor()
        data= cur.execute("select transactions from  data_table"+input("PLEASE: Enter the data_table # from (1->4)  : ")).fetchall()
        return [list(transaction) for transaction in data]

    def initialize_unique_transaction(self) :
        transactions = defaultdict(int)
        for transaction in self.transactions :
            for char in transaction[0] :
                    transactions[char] += 1
        return transactions

    def display_data(self) :
        print("Data_set = {} .".format(self.transactions) )
        print("Unique_Transaction : ")
        for item,sup_count in self.unique_transaction.items() :
            print("                    item : {} , sup_count : {} ".format(item,sup_count))
        print("_________________________")
################################END Of The Class###################################
######################################################################################
class Aporior (Item_Sets):
    def __init__(self  ,min_sup , db_file_name ):
       super().__init__(db_file_name )
       self.min_sup = min_sup
       self.frquent_itemsets = {}
       self.canditates = []

 #////////////////////////////////////////////////////////////////////////////////////
    def Aporior_algorithm(self ) :
        L = []
        for char in self.unique_transaction.keys() :
                if self.unique_transaction[char] >=self.min_sup :
                    self.frquent_itemsets[char]={"sup_count" : self.unique_transaction[char]}
                    L.append(char)      
        while L != [] :
            C = apriori_gen(L)
            self.canditates.append(C)
            L = []
            for transaction in C :
                frequent,sup_count = is_frequent(self.transactions,transaction,self.min_sup) 
                if frequent :                   
                    self.frquent_itemsets["".join(transaction)] ={"sup_count" : sup_count }                  
                    L.append(transaction)
#////////////////////////////////////////////////////////////////////////////////////
    def max_close(self) :
        list1 = []
        list2 = []
        item_sets = sorted(self.frquent_itemsets.keys(),key = len ,reverse=True)
        for item in item_sets :
            if len(item) == len(item_sets[0]) :
                self.frquent_itemsets[item]['maximal'] = True
                self.frquent_itemsets[item]['closed'] = True
                list1.append(item) 
            else :
                maximal = True
                closed  = True
                if  len(list1[0]) - len(item) == 2 :
                    list1 = list2
                    list2 = []    
                list2.append(item)
                for super_set in list1 :               
                    if set(item) <= set(super_set) :
                        maximal = False
                        if self.frquent_itemsets[item]['sup_count'] == self.frquent_itemsets[super_set]['sup_count'] :
                            closed = False
                    if not maximal and not closed :
                        break
                self.frquent_itemsets[item]['maximal'] = maximal
                self.frquent_itemsets[item]['closed'] = closed   
#////////////////////////////////////////////////////////////////////////////////////
    def draw_whole_network(self) :
        network = list(all_subsets(''.join(self.unique_transaction.keys())) )
        g = nx.DiGraph()
        g.add_node('Start',style='filled',fillcolor= "red"  )
        for item in network[1:len(self.unique_transaction)+1] :
            g.add_node(node_data(self.frquent_itemsets , ''.join(item)),style='filled',fillcolor= node_color(self.frquent_itemsets[''.join(item)])  )
            g.add_edge('Start',node_data(self.frquent_itemsets , ''.join(item)))
        for item in network[len(self.unique_transaction)+1:] :
            item = sorted(item)
            item = ''.join(item)
            g.add_node(node_data(self.frquent_itemsets , item),style='filled',fillcolor= node_color(self.frquent_itemsets[item]) if item in self.frquent_itemsets else 'white'  )          
            index1 = index(len(self.unique_transaction),len(item)-2)
            index2 = index(len(self.unique_transaction),len(item)-1)
            
            for item2 in network[int(index1):int(index2)] :   
                item2 = sorted(item2)
                item2 = ''.join(item2)            
                if set(item) >= set(item2) :    
                    g.add_edge(node_data(self.frquent_itemsets , item2),node_data(self.frquent_itemsets , item) )        
        A = to_agraph(g)  
        A.layout('dot')
        A.draw('network.png')  



#///////////////////////////////////////////////////////////////////////////////////
    def draw_frequent_itemsets(self) :
        list1 = []
        list2 = []
        g = nx.DiGraph()
        item_sets = sorted(self.frquent_itemsets.keys(),key = len ,reverse=True)
        for item in item_sets :
            if len(item) == len(item_sets[0]) :         
                g.add_node(node_data(self.frquent_itemsets,item),style='filled',fillcolor=node_color(self.frquent_itemsets[item]) )
                list1.append(item)
            else :
                if  len(list1[0]) - len(item) == 2 :
                    list1 = list2
                    list2 = []    
                list2.append(item)
                g.add_node(node_data(self.frquent_itemsets,item),style='filled',fillcolor=node_color(self.frquent_itemsets[item]))
                for super_set in list1 :               
                    if set(item) <= set(super_set) :    
                        g.add_edge(node_data(self.frquent_itemsets,super_set),node_data(self.frquent_itemsets,item),color ='brown' )                                                
        A = to_agraph(g)  
        A.layout('dot')
        A.draw('frequent.png')              
        
#////////////////////////////////////////////////////////////////////////////////////
    def display_data(self):
        super().display_data()
        print("Min_Support = {} .\n".format(self.min_sup))
        items = sorted(self.frquent_itemsets.keys(),key = len )
        for item in items:
            print("SET = {} : SUP = {} >= min_sup({}) || Maximal : {} - Closed :{}.".format(set(item),self.frquent_itemsets[item]["sup_count"],self.min_sup,self.frquent_itemsets[item]['maximal'],self.frquent_itemsets[item]["closed"]))
 #////////////////////////////////////////////////////////////////////////////////////      
 ############################### END OF THE CLASS ####################################
 ######################################################################################
def has_infrequent_itemset(canditate , frequent_itemsets) :
    canditate_subsets = get_subsets(canditate , len(canditate)-1 )
    for subset in canditate_subsets:
        #print(list(subset) , frequent_itemsets)
        if list(subset) not in frequent_itemsets :
            return True
    return False
#////////////////////////////////////////////////////////////////////////////////////
def get_subsets(Set, m) :
    return list(itertools.combinations(Set,m))
def all_subsets(ss):
  return itertools.chain(*map(lambda x: itertools.combinations(ss, x), range(0, len(ss)+1)))
#////////////////////////////////////////////////////////////////////////////////////
def is_frequent(item_sets , canditate , min_sup ) :
    count = 0
    for transaction in item_sets :
        if set(''.join(canditate)) <= set(transaction[0] ) :
            count += 1
    if count >= min_sup :
        return True,count
    return False,count
#////////////////////////////////////////////////////////////////////////////////////
def apriori_gen(frequent_itemsets) :
    length = len(frequent_itemsets[0])
    if length ==1 :
        for i in range(len(frequent_itemsets)-1) :
            for j in range(i+1,len(frequent_itemsets)) :
                yield sorted([frequent_itemsets[i],frequent_itemsets[j]])
    else : 
        for i in range(len(frequent_itemsets)-1) :
            for j in range(i+1,len(frequent_itemsets)) :            
                if frequent_itemsets[i][:length-1] == frequent_itemsets[j][:length-1] :
                    canditate = list(set(frequent_itemsets[i]).union(set(frequent_itemsets[j])))
                    canditate = sorted(canditate)
                    if not has_infrequent_itemset(canditate , frequent_itemsets) :
                        yield canditate                   
#////////////////////////////////////////////////////////////////////////////////////
def node_data(frequent_itemsets ,node) :
    if node in frequent_itemsets :
        return "{}| {} {}({})".format(node
                                      ,'m' if frequent_itemsets[node]['maximal'] else ''
                                      ,'c' if frequent_itemsets[node]['closed'] and not frequent_itemsets[node]['maximal'] else ''
                                      ,frequent_itemsets[node]['sup_count']
                                      )
    else :
        return node
def node_color(node) :
    if not node['maximal'] and  node['closed'] :
        return 'orange'
    elif node['maximal'] :
        return 'green'
    else :
        return '#CCCCFF'

#////////////////////////////////////////////////////////////////////////////////////

def x(n,_n  ,num) :
    if n == _n-num+1 :
            return n
    else :
            return n * x(n-1,_n,num)
def index(n,num) :
    if num == 0 :
        return 1
    else :
        return index(n,num-1) + (x(n,n,num) / factorial(num))
#////////////////////////////////////////////////////////////////////////////////////
if __name__ == "__main__" :
    obj = Aporior(2,"training_datatset.db")
    obj.Aporior_algorithm()
    obj.max_close()
    obj.draw_whole_network()
    obj.draw_frequent_itemsets()
    obj.display_data()
 
