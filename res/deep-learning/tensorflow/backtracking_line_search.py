from matplotlib.pyplot import figure, hold, plot, show, xlabel, ylabel, legend

def f(x):
    return (x-3)**2
def f_grad(x):
    return 2*(x-3)

# gradient descent
x = 0
y = f(x)
err = 1.0
maxIter = 300
curve = [y]
it = 0
step = 0.1
while err > 1e-4 and it < maxIter:
    it += 1
    gradient = f_grad(x)
    new_x = x - gradient * step
    new_y = f(new_x)
    new_err = abs(new_y - y)
    if new_y > y:  # reduce step size if there is sign of divergence
        step *= 0.8
    err, x, y = new_err, new_x, new_y
    print('err:', err, ', y:', y)
    curve.append(y)

print('iterations: ', it)
figure()
plot(curve, 'r*-')
xlabel('iterations')
ylabel('objective function value')