import sys
import numpy as np
import math
from collections import Counter

# Funcao que le o arquivo de entrada

def readFile():
    name = sys.argv[1]          # Le arquivo de entrada da linha de comando
    file  = open(name, "r")     # Abre arquivo em modo de leitura
    lines = file.readlines()	# Le todas as linhas do arquivo
    file.close()                # Fecha o arquivo
    return lines

def getA(tableau,restrictions):
	return tableau[1:,restrictions:-1]

def getB(tableau,restrictions):
	return tableau[1:,-1]

def getC(tableau,restrictions):
	return tableau[0,restrictions:-1]

def getZ(tableau,restrictions):
	return tableau[0,-1]

def getCertificate(tableau,restrictions):
	return tableau[0,0:restrictions]

def putInFPI(A,b,c,operations,negativity,restrictions):      
    
    # Verifica igualdades      
    for i in range(0,len(operations)):          # Percorre todas as linhas dos simbolos de igualdade/desigualdade
    	if(operations[i] != '=='):
        	newColumn = np.empty((restrictions,1))
        	c.append(float(0.0))
    	if(operations[i] == '<='):          # Se for <=
        	for j in range(0,restrictions): # Percorre todas as restricoes
        		# Adiciona variável de folga positiva se for a linha do <=
        		if(j == i):
        			newColumn[j] = float(1.0)
        		else:
        			# Adiciona 0 se nao for
        			newColumn[j] = float(0.0)
        	A = np.concatenate((A,newColumn),axis = 1)

    	if(operations[i] == '>='):			# Se for >=
        	for j in range(0,restrictions): # Percorre todas as restricoes
        		# Adiciona variável de folga negativa se for a linha do >=
           		if(j == i):
           			newColumn[j] = float(-1.0)
           		else:
           			# Adiciona 0 se nao for
           			newColumn[j] = float(0.0)	
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

def assemblesTableau(tableau,restrictions,c):
	# Lista com indices das colunas da base viável
	jBase = []

	# Pega somente o A do tableau
	A = getA(tableau,restrictions)

	# Pega o c do tableau que sera alterado
	cOld = getC(tableau,restrictions)

	# Percorre o A/c do tableau atual

	for j in range(0,np.size(A,1)):
		# Se encontrar um c 0
		if(cOld[:,j] == 0):
			# Verifica se abaixo do c 0 tem 1 um e a quantidade de restricoes-1 em 0's
			if(list(A[:,j]).count(1) == 1 and list(A[:,j]).count(0) == restrictions-1):
				jBase.append(j+restrictions) # Achou coluna básica, salva o indice dela


	# Adiciona 0 no c para salvar o resultado da PL
	c.append(float(0.0))

	# Transforma c em numpy matrix
	c = np.matrix(c)

	# Mutiplica c por -1 para add ao tableau
	c = c*-1

	# Gera a quantidade de zeros para adicionar "envolta" do c
	z = np.matrix(np.zeros(np.size(tableau,0)-1))

	c = np.concatenate((z,c), axis = 1)

	c = np.concatenate((c,z), axis = 1)
	    
	# Adiciona c antigo no tableau

	tableau = np.vstack([c,tableau[1:,:]])

	# Percorre todas as colunas que tem colunas básicas
	for j in jBase:
		# Percorre todas as linhas do tableau
		for i in range(0,np.size(tableau,0)):
			# Procura qual linha tem o valor 1
			if(tableau[i,j] == 1):
				# Faz o c do tableau - a linha vezes o valor do c
				tableau[0] = tableau[0] - (tableau[i]*tableau[0,j])
	
	# Remove colunas do tableau correspondentes a variaveis extras da auxiliar

	tableau = np.concatenate((tableau[:,0:np.size(tableau,1)-(restrictions+1)],tableau[:,-1]),axis = 1)

	return tableau
    
                
def assemblesTableauAuxiliar(A,b,c):
	# Transforma b em numpy matrix e o transpoe
	b = np.matrix(b).T  

	# Adiciona 0 em cima do b para salvar o resultado da PL (sera usado em baixo)
	b0 = np.vstack([np.zeros(1),b])

	# Transforma c em vetor de zeros
	c = np.zeros(len(c)+1)

	# Coloca c no tableau
	mat = np.vstack([c,np.concatenate((A,b), axis = 1)])
	
	# Gera uma matriz identidade com a mesma quantidade de linhas da matriz
	I = np.identity(np.size(mat,0)-1)
	
	# Coloca zeros acima da matriz identidade
	I1 = np.vstack([np.zeros(np.size(mat,0)-1),I])

	# Coloca um's acima da matriz identidade
	I2 = np.vstack([np.ones(np.size(mat,0)-1),I])
	
	# Coloca a matriz identidade + zeros a esquerda da matriz original
	tableau = np.concatenate((I1,mat), axis = 1)   

	# Coloca a matriz identidade + ums a direita da matriz original	   	
	tableau = np.concatenate((tableau[:,0:-1],I2), axis = 1)

	# Coloca o b no tableau	
	tableau = np.concatenate((tableau,b0), axis = 1)

	# Faz subtracao da primeira linha do tableau com a soma de todas as outras
	tableau[0] = tableau[0] - tableau[1:].sum(axis = 0)
	
	return tableau

# Funcao que corrige "zeros negativos"
def correctZeros(mat):
	for i in range(0,np.size(mat,0)): 		# Percorre todas as linhas da matriz
		for j in range(0,np.size(mat,1)):	# Percorre todas as colunas da matriz
			if mat[i,j] == -0:				# Se encontrar -0 ou 0 cai aqui
				mat[i,j] = abs(0) 			# Faz todo zero ser zero valor absoluto
	return mat

# Funcao que pivoteia uma matriz dado um par de linha e coluna
def pivote(lin,col,mat):

	mat[lin] = mat[lin] / float(mat[lin,col]) 	# Divide linha a ser pivoteada pelo pivot

	for i in range(0,np.size(mat,0)):			# Percorre as linhas da matriz. size(mat,0) pega quantidade de linhas
		if i != lin:							# Se a linha em questao nao for a do pivo			
			# Faz a linha atual menos a linha do pivo * o "pivo" equivalente da linha atual mas da coluna do pivo original
			mat[i] = mat[i] - (mat[lin]*mat[i,col])	
	mat = correctZeros(mat)
	return mat

def choosePivot(mat,restrictions):
	lin = -1
	col = -1
	j = 0

	menor = 999999 
	bCond = True
	cCond = True
	found = False

	c = getC(mat,restrictions)	# Separa o c da matriz	
	b = getB(mat,restrictions)	# Separa o b da matriz	
	A = getA(mat,restrictions)	# Separa o A da matriz

	while(not(found) and j < np.size(c,1)): # Percorre vetor c
		menor = 999999 
		if c[0,j] < 0:				# Encontra primeiro c negativo, 
			col = j+np.size(A,0)	# Soma a quantidade de linhas de A pois o indice final deve considerar o tableau completo
			for i in range(0,np.size(b,0)):							# Percorre vetor b
				if A[i,col-np.size(A,0)] > 0:						# Procura um A[i,j] positivo			
					if (b[i,0] / A[i,col-np.size(A,0)]) < menor: 	# Verifica se a divisao do b correspondente a linha e coluna atual eh o menor
						menor = b[i,0] / A[i,col-np.size(A,0)]		# Se for o menor torna ele o novo menor
						lin = i+1									# Soma 1 a linha pois o indice final deve considerar o tableau completo
						found = True
		j = j +1
						

	# for j in range(0,np.size(c,1)): # Percorre vetor c
	# 	menor = 999999 
	# 	if c[0,j] < 0:				# Encontra primeiro c negativo, 
	# 		col = j+np.size(A,0)	# Soma a quantidade de linhas de A pois o indice final deve considerar o tableau completo
	# 		break

	# for i in range(0,np.size(b,0)):						# Percorre vetor b
	# 	if A[i,col-np.size(A,0)] > 0:						# Procura um A[i,j] positivo			
	# 		if (b[i,0] / A[i,col-np.size(A,0)]) < menor: 	# Verifica se a divisao do b correspondente a linha e coluna atual eh o menor
	# 			menor = b[i,0] / A[i,col-np.size(A,0)]		# Se for o menor torna ele o novo menor
	# 			lin = i+1									# Soma 1 a linha pois o indice final deve considerar o tableau completo
						


	
		

	for i in range(0,np.size(b,0)): # Percorre vetor b
		if b[i,0] < 0:				
			bCond = False

	for j in range(0,np.size(c,1)): # Percorre vetor c
		if c[0,j] < 0:
			cCond = False

	if bCond and cCond:# and achaSolucao(mat):
		return False,lin,col
	elif (not bCond) or (not cCond): # or (not achaSolucao(mat)):
		return True,lin,col

def findSolution(tableau,restrictions,variables):
	jBase = []

	A = getA(tableau,restrictions)
	c = getC(tableau,restrictions)
	b = getB(tableau,restrictions)

	# Percorre o A e c
	for j in range(0,np.size(A,1)):
		# Se encontrar um c 0
		if(c[:,j] == 0):
			# Verifica se abaixo do c 0 tem 1 um e a quantidade de restricoes-1 em 0's
			if(list(A[:,j]).count(1) == 1 and list(A[:,j]).count(0) == restrictions-1):
				jBase.append(j) 		# Achou coluna básica, salva o indice dela

	# Gera uma matriz para salvar a base viavel
	base = np.matrix(np.ones((restrictions,restrictions)))	

	# Percorre os indices da base viavel na matriz A e salva as colunas na matriz base
	jB = 0
	for j in jBase:
		base[:,jB] = A[:,j]
		jB = jB + 1

	# Calcula solucao

	sol = np.matmul(base,b)

	x = []

	jB = 0
	for j in range(0,np.size(c,1)):
		if(c[:,j] == 0 and list(A[:,j]).count(1) == 1 and list(A[:,j]).count(0) == restrictions-1):
			x.append(float(sol[jB,:]))
			jB = jB + 1
		else:
			x.append(0)

	return x[0:variables]

def verifyStatus(tableau):
	return 'otimo'

def saveFile(status,z,x,certificate):
	name = sys.argv[2]                  # Le arquivo de saida da linha de comando
	file  = open(name, "w")				# Abre arquivo em modo de escrita

	if(status == 'otimo'):
		file.write('Status: otimo\n')
		file.write('Objetivo: ' + str(z) + '\n')
		file.write('Solucao:\n')
		for xi in x:
			file.write(str(xi) + ' ')
		file.write('\nCertificado:\n')		
		for j in range(0,np.size(certificate,1)):
			file.write(str(certificate[0,j]) + ' ')
	file.close()                          # Fecha o arquivo

def main(verbose):    
	np.set_printoptions(linewidth = 200)
	
	cont = 0
	retorno = True
	i = 0
	j = 0
	zero = 0.00001
	z = 0

	matrix = []
	lineMatrix = []
	A = []
	b = []
	c = []
	x = []
	operations = []
	
	lines = readFile()
	variables = int(lines[0])
	restrictions = int(lines[1])
	negativity = list(map(int,lines[2].replace('\n','').split(' ')))
	c = list(map(float,lines[3].replace('\n','').split(' ')))

	for line in lines[4:]:
		matrix.append(list(line.replace('\n','').split(' ')))
		lineMatrix = []
		for i in range(0,variables):
			lineMatrix.append(float(matrix[-1][i]))
		A.append(lineMatrix)
		operations.append(matrix[-1][-2])
		b.append(float(matrix[-1][-1]))


	if(verbose):
		print('A lido do arquivo:\n',A,'\n')
		print('b lido do arquivo:\n',b,'\n')
		print('c lido do arquivo:\n',c,'\n')
		

	A = np.matrix(A)
	A,b,c = putInFPI(A,b,c,operations,negativity,restrictions)

	if(verbose):
		print('\n\nA em FPI:\n',A,'\n')
		print('b em FPI:\n',b,'\n')
		print('c em FPI:\n',c,'\n')


	tableau = assemblesTableauAuxiliar(A,b,c)

	if(verbose):
		print('\n\nTableau da matriz auxiliar montado:\n',np.array_str(tableau,precision = 5, suppress_small = True),"\n")


	# Resolve matriz auxiliar
		
	while retorno and i != -1 and j != -1:
		retorno,i,j = choosePivot(tableau,restrictions)	
		if i != -1 and j != -1: 
			tableau = pivote(i,j,tableau)
			cont = cont + 1
			if(verbose):
				print('\n\nPivoteamento :',cont,' :\n',np.array_str(tableau,precision = 2, suppress_small = True),"\n")


	if(getZ(tableau,restrictions) <= zero):
		tableau = assemblesTableau(tableau,restrictions,c)
		if(verbose):
			print('\nMatriz auxiliar Alterada :\n',np.array_str(tableau,precision = 2, suppress_small = True),"\n")
		retorno = True
		i = 0
		j = 0
		cont = 0
		while retorno and i != -1 and j != -1:
			retorno,i,j = choosePivot(tableau,restrictions)	
			if i != -1 and j != -1: 
				tableau = pivote(i,j,tableau)
				cont = cont + 1
				if(verbose):
					print('\n\nPivoteamento :',cont,' :\n',np.array_str(tableau,precision = 2, suppress_small = True),"\n")

	status = verifyStatus(tableau)

	if(status == 'otimo'):
		x = findSolution(tableau,restrictions,variables)
		z = getZ(tableau,restrictions)
		certificate = getCertificate(tableau,restrictions)

	print(certificate)

	saveFile(status,z,x,certificate)
	
	
main(True)	
