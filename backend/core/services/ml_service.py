from sklearn.linear_model import LinearRegression


class PredictionService:

    def train_and_predict(self, values):

        X = []
        y = []

        for index, item in enumerate(values):
            X.append([index + 1])
            y.append(item)

        if len(X) < 2:
            return Response({
                "error": "Not enough data for prediction"
            })

        model = LinearRegression()

        model.fit(X, y)

        next_day = [[len(X) + 1]]

        prediction = model.predict(next_day)

        return float(prediction[0])