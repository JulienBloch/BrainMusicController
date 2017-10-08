import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt

off_data = np.genfromtxt('museOff2.csv', delimiter=',', skip_header=1)
on_data = np.genfromtxt('museOn2.csv', delimiter=',', skip_header=1)

# alphas = [off_data[:,8], on_data[:,8]]
for i in range(8, 12):
	print('alpha, off vs on')
	print(np.mean(np.exp(off_data[:,i])))
	print(np.mean(np.exp(on_data[:,i])))

plt.plot(np.mean(np.exp(off_data[:,8])))

eye_data = np.genfromtxt('museEyes.csv', delimiter=',', skip_header=1)

a = np.exp(eye_data)[:,:-1]
b = eye_data[:,-1]

sol = np.dot(inv(np.dot(a.T, a)), (np.dot(a.T, b)))
print(sol)

# test_data = np.genfromtxt('museOpenTest.csv', delimiter=',', skip_header=1)

test_data = np.genfromtxt('museClosedTest.csv', delimiter=',', skip_header=1)
test_data = np.exp(test_data)

print(test_data.shape)
num_open = 0

for row in test_data:
	z = 0
	for i in range(len(row)):
		z+= row[i] * sol[i]
	# print(z)
	if (z <0):
		num_open += 1

print("accuracy is: " + str(num_open/test_data.shape[0]))


