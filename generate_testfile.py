import os
import random

if __name__ == '__main__':
	f = open('input','w')
	f_add = open('input_add','w')
	f_ndd = open('ndds','w')
	num_of_nodes = 20
	num_of_addnodes = 10
	num_of_ndd =5
	num_of_iter =10
	default_weight=1

	for i in range(num_of_nodes):
		list_nodes = []
		for it in range(num_of_iter):
			num_of_edges = random.randint(0,num_of_nodes-1)
			if(num_of_edges not in list_nodes):
				list_nodes.append(num_of_edges)
				weight = random.random()
				f.write(str(i) +'	' + str(num_of_edges)+'	'+ str(weight)+ '\n')


	for i in range(num_of_addnodes):
		list_nodes = []
		for it in range(num_of_iter):
			num_of_edges = random.randint(0,num_of_nodes-1)
			if(num_of_edges not in list_nodes):
				list_nodes.append(num_of_edges)
				weight = random.random()
				flip_coin = random.random()
				if flip_coin >0.3:
					f_add.write(str(i+num_of_nodes) +'	' + str(num_of_edges)+'	'+ str(weight)+ '\n')
				else:
					f_add.write(str(num_of_edges) +'	' + str(i+num_of_nodes)+'	'+ str(weight)+ '\n')
	
	for i in range(num_of_ndd):
		list_nodes = []
		for it in range(num_of_iter):
			num_of_edges = random.randint(0,num_of_nodes-1)
			if(num_of_edges not in list_nodes):
				list_nodes.append(num_of_edges)
				weight = random.random()
				f_ndd.write(str(i) +'	' + str(num_of_edges)+'	'+ str(weight)+ '\n')









