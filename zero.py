# thislist = ['яблоко', 'банан', 'вишня']
# # thislist.insert(2, 'арбуз')
# list1 = [x for x in thislist]
# list1 = [x.upper() for x in thislist]
# list1 = [x if x != 'банан' else 'апельсин' for x in thislist]
# print(list1)
# onelist = [x for x in thislist if 'н' in x]
# print(onelist)
# thislist.insert(3, 'yess')
# thislist[0:2] = ['nooo', 'oneee']
# tropical = ['qiwi', 'ananas', 'orex']
# thislist.extend(tropical)
# [print(x) for x in thislist]
# print(thislist)
# thislist.remove('qiwi')
# thislist.pop(1)
# thislist.pop()
# del thislist[0]
# thislist.clear()
# print(thislist)
#
#
# for x in thislist:
#     print(x)

# newlist = []
#
# for x in thislist:
#     if 'а' in x:
#         newlist.append(x)
# print(newlist)




# thislist = ["апельсин", "манго", "киви", "ананас", "банан"]
# thislist.sort(reverse=True)
# print(thislist)
# thislist.sort()
# print(thislist)

# list1 = [100, 50, 65, 82, 23]
# list1.sort()
# print(list1)


def myfunc(n):
    return abs(n - 50)

thislist = [100, 50, 65, 82, 23]
thislist.sort(key=myfunc)
print(thislist)



