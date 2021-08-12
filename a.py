import numpy as np



a = np.array([[0, 1, 2, 3],
       [4, 5, 6, 7],
       [8, 9, 10, 11]])
b = np.array(a < 5)

d = np.array([0, 1, 2, 3])

c = np.array([l[:2] for l in a[1:3]])

e = np.ravel(a)

print(len(e))