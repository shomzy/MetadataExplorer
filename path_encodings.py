ROOT = 0
LIST = 1
LIST_KEY = 2
DICT = 3


'''
(LIST)__(LIST_KEY)
(LIST_KEY)__(DICT)
(DICT)__(KEY)
(KEY)_(LIST)
(KEY)_(DICT)
(ROOT)__(DICT)  

From this we can assert that following:
1. LIST there will only be a LIST_KEY with any value
2. LIST_KEY there will be any value
3. DICT there will only be a KEY with any value
4. KEY there will be any value
5. ROOT there will be only a DICT
'''
