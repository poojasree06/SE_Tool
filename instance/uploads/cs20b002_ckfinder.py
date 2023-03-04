from itertools import combinations

#generating candidate keys
def generate_candidate_keys(attributes,functional_dependencies):
    # generating all subsets of attributes
    powerset=find_powerset(attributes)
    super_keys=set()
    candidate_keys=set()
    for subset in powerset:
        # computing closure of each subset
        closure=compute_closure(subset,functional_dependencies)
        # if closure equals to attributes then take it as a super key
        if(len(set(attributes).difference(closure))==0):
            super_keys.add(subset) 
    
    # finding candidate keys - get minimum length keys from super keys
    length=len(min(super_keys,key=len))
    for each in super_keys:
        if(len(each)==length):
            candidate_keys.add(each)
    return candidate_keys

# finding essential keys - keys that must be present in the candidate key
def find_essential_keys(attributes,functional_dependencies):
    essential_keys=set()
    for fd in functional_dependencies:
        split_attributes=list(fd[1])
        for attribute in split_attributes:
            essential_keys.add(attribute)
    essential_keys=set(attributes).difference(essential_keys)
    return essential_keys
    
# computing clousre of attribute
def compute_closure(A,fds):
    closure=set(A)
    while True:
        previous_closure=closure.copy()
        for fd in fds:
            if set(fd[0]).issubset(closure):
                closure.update(set(fd[1]))
        if closure ==previous_closure:
            break
    return closure

# finding all subsets
def find_powerset(attributes):
    powerset=[]
    for r in range(len(attributes)+1):
        for combination in combinations(attributes, r):
            if(len(combination)!=0):
                powerset.append(combination)
    return powerset

# attributes=['A','B','C','D','E','F']
# no_of_attributes=6
# functional_dependencies=[('A','BC'),('AB','E'),('C','DE'),('E','A')]

# take file as input
fil=input("enter text filename: ")
try:
    lines_list=[]
    with open(fil, 'r') as fp:
        line = fp.readline()
        while line != '':
            lines_list.append(line.strip())
            line = fp.readline()

except FileNotFoundError:
    print("Please check the path")

# attributes
attributes=list(lines_list[0])
# no of functional dependencies
no_of_fd=int(lines_list[1])
# functional dependencies
functional_dependencies=[]
for i in range(0,no_of_fd):
    x=lines_list[i+2]
    functional_dependencies.append(tuple(x.split(', ')))

# print("Attributes")
# print(attributes) 
# print("Functional dependencies")
# # print(functional_dependencies)
# for fd in functional_dependencies:
#     print(f'{fd[0]}->{fd[1]}')

essential_keys=find_essential_keys(attributes,functional_dependencies)
closure=compute_closure(essential_keys,functional_dependencies)

print('Candidate Keys')
if(len(set(attributes).difference(closure))==0):
    essential_keys=''.join(essential_keys)
    print(essential_keys)
else:
    candidate_keys=generate_candidate_keys(attributes,functional_dependencies)
    for keys in sorted(list(candidate_keys)):
        keys=''.join(keys)
        print(keys)


