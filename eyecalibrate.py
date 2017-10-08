import numpy as np
from numpy.linalg import inv

eye_data = np.genfromtxt('data/museEyes.csv', delimiter=',', skip_header=1)

a = np.exp(eye_data)[:,:-1]
b = eye_data[:,-1]

sol = np.dot(inv(np.dot(a.T, a)), (np.dot(a.T, b)))
print(sol)
np.savetxt("weights.csv", sol, delimiter=",")