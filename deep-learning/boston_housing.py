from keras.models import Sequential
from keras.layers import Dense
from keras.datasets import boston_housing


(X_train, Y_train), (X_test, Y_test) = boston_housing.load_data()

nFeatures = X_train.shape[1]

model = Sequential()
model.add(Dense(1, input_shape=(nFeatures,), activation="linear"))

model.compile(optimizer="rmsprop", loss="mse", metrics=["mse", "mae"])

model.fit(X_train, Y_train, batch_size=4, epochs=1000)

model.summary()

model.evaluate(X_test, Y_test, verbose=True)

Y_pred = model.predict(X_test)

print(Y_test[:5])
print(Y_pred[:5,0])

