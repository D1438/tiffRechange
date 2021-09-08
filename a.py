import numpy as np
import sys


a = np.array([[0, 1, 2, 3],
       [4, 5, 6, 7],
       [8, 9, 10, 11]])
b = np.array(a < 5)

d = np.array([0, 1, 2, 3])

#m = np.array([[[0, 1], [2, 3]], [[4, 5], [6, 7]]])

m = np.array([[[0 for i in range(3)] for j in range(3)] for k in range(3)])
count = 0

for i in range(0, 3):
       for j in range(0, 3):
              for k in range(0, 3):
                     m[i][j][k] = count
                     count += 1

c = np.array([l[:2] for l in a[1:3]])

e = np.ravel(a)

#print(len(e))
print(type(float(sys.argv[len(sys.argv) - 1])))

print(np.all(a == 2))

print(m[0][0])