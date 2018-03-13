import sqlite3
import itertools
import networkx as nx
import matplotlib.pyplot as plt
#################################################################################
class Item_Sets :
    def __init__(self , db_file_name , unique_transaction  ) :
        self.unique_transaction = [x for x in unique_transaction]
        self.transactions = self.initialize_transactions(db_file_name)
       
    def initialize_transactions(self,db_file_name) :
        conn = sqlite3.connect(db_file_name)
        cur  = conn.cursor()
        data= cur.execute("select transactions from  data_table"+input("PLEASE: Enter the data_table # from (1->4)  : ")).fetchall()
        return [list(transaction) for transaction in data]

    def display_data(self) :
        print("Data_set = {} .".format(self.transactions) )
        print("Unique_Transaction = {} .".format(self.unique_transaction) )
        print("_________________________")
########################################################################################
class Frequent_itemsets :
    def __init__(self , itemset , sup_count ) :
        self.itemset = itemset
        self.sup_count = sup_count
        self.maximal = False
        self.colsed = False 
######################################################################################
class Aporior (Item_Sets):
    def __init__(self  ,min_sup , db_file_name , unique_transaction):
       super().__init__(db_file_name , unique_transaction)
       self.min_sup = min_sup
       self.frquent_itemsets = []
       self.canditates = []
       self.frequent_graph = nx.Graph()
 #////////////////////////////////////////////////////////////////////////////////////
    def Aporior_algorithm(self ) :
        L = []
        for char in self.unique_transaction :
                frequent,sup_count = is_frequent(self.transactions,char ,self.min_sup) 
                if frequent :
                    self.frquent_itemsets.append(Frequent_itemsets(set(char),sup_count))
                    L.append(char)      
        while L != [] :
            C = apriori_gen(L)
            self.canditates.append(C)
            L = []
            for transaction in C :
                frequent,sup_count = is_frequent(self.transactions,transaction,self.min_sup) 
                if frequent :
                    self.frquent_itemsets.append(Frequent_itemsets(set(transaction),sup_count))
                    L.append(transaction)
#////////////////////////////////////////////////////////////////////////////////////
    def max_close(self) :
        list1 = []
        list2 = []
        for i in range(len(self.frquent_itemsets)-1,-1,-1) :
            if len(self.frquent_itemsets[i].itemset ) == len(self.frquent_itemsets[-1].itemset) :
                self.frquent_itemsets[i].maximal = True
                self.frquent_itemsets[i].closed = True
                self.frequent_graph.add_node(''.join(self.frquent_itemsets[i].itemset),sup_count = self.frquent_itemsets[i].sup_count)
                list1.append(self.frquent_itemsets[i])                
            else :
                maximal = True
                closed  = True
                if  len(list1[0].itemset) - len(self.frquent_itemsets[i].itemset ) == 2 :
                    list1 = list2
                    list2 = []
                list2.append(self.frquent_itemsets[i])
                self.frequent_graph.add_node(''.join(self.frquent_itemsets[i].itemset),sup_count = self.frquent_itemsets[i].sup_count)
                for item in list1 :               
                    if self.frquent_itemsets[i].itemset <= item.itemset :
                        maximal = False
                        self.frequent_graph.add_edge(''.join(item.itemset),''.join(self.frquent_itemsets[i].itemset))
                        if self.frquent_itemsets[i].sup_count == item.sup_count :
                            closed = False
                    if not maximal and not closed :
                        break
                self.frquent_itemsets[i].maximal = maximal
                self.frquent_itemsets[i].closed = closed
#////////////////////////////////////////////////////////////////////////////////////
    def draw_frequent_itemsets(self) :
        color_map = []
        item_sets=self.frquent_itemsets
        pos = nx.spring_layout(self.frequent_graph)

        for node in self.frequent_graph :
            for x in item_sets :
                if node == ''.join(x.itemset) :
                    if x.closed and not x.maximal :
                        color_map.append('red')                                           
                    elif x.maximal :
                        color_map.append('blue')
                    else :
                        color_map.append('green')
                    item_sets.remove(x)
                    break      
        nx.draw(self.frequent_graph,pos,node_color = color_map , with_labels = True,node_size=1300)
        for node in self.frequent_graph:
            x,y=pos[node]
            plt.text(x,y+0.1,s=self.frequent_graph.node[node]['sup_count'], bbox=dict(facecolor='white', alpha=0.5),horizontalalignment='center')         
        
        plt.show()
#////////////////////////////////////////////////////////////////////////////////////
    def display_data(self):
        super().display_data()
        print("Min_Support = {} .\n".format(self.min_sup))
        for Set in self.frquent_itemsets:
            print("SET = {} : SUP = {} >= min_sup({}) || Maximal : {} - Closed : {} .".format(Set.itemset,Set.sup_count,self.min_sup,Set.maximal,Set.closed))
 #////////////////////////////////////////////////////////////////////////////////////      
 ############################### END OF THE CLASS ####################################

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
#////////////////////////////////////////////////////////////////////////////////////
def is_frequent(item_sets , canditate , min_sup ) :
    count = 0
    for transaction in item_sets :
        #print(transaction[0])
        if set(''.join(canditate)) <= set(transaction[0] ) :
            count += 1
            #print(''.join(canditate) , count  )
    #print(''.join(canditate) , count )
    if count >= min_sup :
        return True,count
    return False,count
#////////////////////////////////////////////////////////////////////////////////////
def apriori_gen(frequent_itemsets) :
    canditates = []
    length = len(frequent_itemsets[0])
    if length ==1 :
        for i in range(len(frequent_itemsets)-1) :
            for j in range(i+1,len(frequent_itemsets)) :
                canditates.append([frequent_itemsets[i],frequent_itemsets[j]])
    else : 
        for i in range(len(frequent_itemsets)-1) :
            for j in range(i+1,len(frequent_itemsets)) :            
                if frequent_itemsets[i][:length-1] == frequent_itemsets[j][:length-1] :
                    canditate = list(set(frequent_itemsets[i]).union(set(frequent_itemsets[j])))
                    canditate = sorted(canditate)
                    if not has_infrequent_itemset(canditate , frequent_itemsets) :
                        canditates.append(canditate)                   
    return canditates
#////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////

if __name__ == "__main__" :
    obj = Aporior(2,"training_datatset.db","ABCDE")
    obj.Aporior_algorithm()
    obj.max_close()
    obj.display_data()
    obj.draw_frequent_itemsets()
 