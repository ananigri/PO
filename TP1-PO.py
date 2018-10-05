import sys
import numpy as np
import math
from collections import Counter

# Funcao que le o arquivo de entrada

def readFile():
    name = sys.argv[1]                   # Le arquivo de entrada da linha de comando
    arq  = open(name, "r")               # Abre arquivo em modo de leitura
    lines = arq.readlines()             # Le todas as linhas do arquivo
    arq.close()                          # Fecha o arquivo
    return lines

def putInFPI(A,b,c,operations,negativity,restrictions):      
    
    # Verifica igualdades      
    for i in range(0,len(operations)):          # Percorre todas as linhas dos simbolos de igualdade/desigualdade

        newColumn = np.empty((restrictions,1))
        c.append(0)
        if(operations[i] == '<='):          # Se for <=

        	for j in range(0,restrictions): # Percorre todas as restricoes
        		# Adiciona variável de folga positiva se for a linha do <=
        		if(j == i):
        			newColumn[j] = 1
        		else:
        			# Adiciona 0 se nao for
        			newColumn[j] = 0
        	A = np.concatenate((A,newColumn),axis = 1)

        if(operations[i] == '>='):			# Se for >=
        	for j in range(0,restrictions): # Percorre todas as restricoes
        		# Adiciona variável de folga negativa se for a linha do >=
           		if(j == i):
           			newColumn[j] = -1
           		else:
           			# Adiciona 0 se nao for
           			newColumn[j] = 0	
        	A = np.concatenate((A,newColumn),axis = 1)



    neg = len(negativity) 
    j = 0

                
    # Verifica nao negatividade
    while neg > 0:                               # Percorre todas as colunas de negatividade
        if(negativity[j] == 0):                  # Se uma variavel for livre 
            neg = neg + 1
            newC = c[0:j+1]                      # Atualiza o da seguinte forma:
            newC.append(c[j]*(-1))               # Se c = [1, 2, 3] e variavel 2 eh livre -> c = [1,2,-2,3]
            c = newC + c[j+1:]
            newA = A[:,0:j+1]
            newA = np.concatenate((newA,A[:,j]*(-1)),axis = 1) 
            A = np.concatenate((newA,A[:,j+1:]),axis = 1)
            negativity[j] = 1
            newNeg = negativity[0:j+1]                      
            newNeg.append(1)               
            negativity = newNeg + negativity[j+1:]
        j = j + 1
        neg = neg - 1
        
    # Verifica se b é negativo e caso seja multiplica a linha toda por -1
    
    for i in range(0,len(b)):
        if(b[i] < 0):
            b[i] = b[i]*(-1)
            A[i] = A[i]*(-1)
         
    return A,b,c
    
                
def assemblesTableau(A,b,c):
	# Transforma b em numpy matrix e o transpoe
	b = np.matrix(b).T  
	# Adiciona 0 em cima do b para salvar o resultado da PL (sera usado em baixo)
	b0 = np.vstack([np.zeros(1),b])
	    
	# Adiciona 0 no c para salvar o resultado da PL
	c.append(0)
	# Transforma c em numpy matrix
	c = np.matrix(c)
	
	# Multiplica c por -1 para add no 
	c = c*(-1)
	mat = np.vstack([c,np.concatenate((A,b), axis = 1)])
	
	# Gera uma matriz identidade com a mesma quantidade de linhas da matriz
	I = np.identity(np.size(mat,0)-1)
	
	# Coloca zeros acima da matriz identidade
	I = np.vstack([np.zeros(np.size(mat,0)-1),I])
	
	# Coloca a matriz identidade + zeros a esquerda da matriz original
	tableau = np.concatenate((I,mat), axis = 1)   
	   	
	tableau = np.concatenate((tableau[:,0:-2],I), axis = 1)
	
	tableau = np.concatenate((tableau,b0), axis = 1)
	
	return tableau

def main():    
	np.set_printoptions(linewidth = 200)
	
	matrix = []
	lineMatrix = []
	A = []
	b = []
	c = []
	operations = []
	
	lines = readFile()
	variables = int(lines[0])
	restrictions = int(lines[1])
	negativity = list(map(int,lines[2].replace('\n','').split(' ')))
	c = list(map(int,lines[3].replace('\n','').split(' ')))

	for line in lines[4:]:
		matrix.append(list(line.replace('\n','').split(' ')))
		lineMatrix = []
		for i in range(0,variables):
			lineMatrix.append(int(matrix[-1][i]))
		A.append(lineMatrix)
		operations.append(matrix[-1][-2])
		b.append(int(matrix[-1][-1]))
		

	A = np.matrix(A)
	A,b,c = putInFPI(A,b,c,operations,negativity,restrictions)

	tableau = assemblesTableau(A,b,c)

	print(tableau)
  	  	
  	
	
main()	
