import numpy as np
import sys
import glob, datetime
"""
a = 31
n = datetime.datetime(2021, 4, a-3)
l = []

for i in range(7):
       pattern = n.strftime('%m-%d*')
       print(pattern)
       l += glob.glob(pattern)
       n += datetime.timedelta(days=1)
"""

#print(len(sys.argv))
#print(sys.argv[len(sys.argv) - 1])

a = np.array([[0, 1, 2, 3],
       [4, 5, 6, 7],
       [8, 9, 10, -1000]])
b = np.array(a < 5)

d = np.array([0, 1, 2, 3])

#m = np.array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]])

m = np.array([[[0 for i in range(2)] for j in range(2)] for k in range(3)])
m[2][1][0] = 1
count = 1

#np.savetxt("/Users/ishizawadaisuke/Documents/graduate/temperture/proc-comp/op_80.csv", a, delimiter=",", fmt = '%d')

c = np.array([l[:2] for l in a[1:3]])

e = np.ravel(a)

if np.any(a == -1000) == True and np.any(a > -5):
       print("うわああああああい！")

#print(len(e))
#print(int(count/80))
#print(m)