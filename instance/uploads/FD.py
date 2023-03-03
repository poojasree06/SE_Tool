'''Finding candidate keys from Functional Dependencies'''

print('Enter attribute names of the relation')
attributes=input().replace(' ','').split(',')

print('Enter functional dependencies')
FD_list={}   # list of functional dependencies
while True:
    FD=input().replace(' ','').split('->')
    if FD == '':               # ENTERED WITHOUT A VALUE ,BREAK OUT OF THE LOOP
        break
    else:
        FD_list[FD[0]]=FD[1]


attributes=['A','B','C','D','E','F','G']
FD_list={
    'AB':'CD',
    'AF':'D',
    'DE':'F',
    'C':'G',
    'F':'E',
    'G':'A'
}

attributes=['A','B','C','D','E','F']
# no_of_attributes=4
FD_list={
    'A':'BC',
    'AB':'E',
    'C':'DE',
    'E':'A'
}

def split_name(x):
    res=[]
    for i in range(len(x)):
        res.extend(x[i])
    return res

def  closure(A,FD_list):
    S=[]
    S.extend(A)
    return set(S)

S=closure(attributes[0],FD_list)
print(S)
    
    


