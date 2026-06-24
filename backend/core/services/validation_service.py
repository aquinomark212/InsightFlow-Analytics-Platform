class PredictionValidationService:

    def calculate_error(self, actual, predicted):

        absolute_error = abs(actual - predicted)
        percent_error = 0

        if actual > 0:
            percent_error = (absolute_error / actual) * 100


        return {
            "actual": actual,
            "predicted": round(predicted, 2),
            "absolute_error": round(
                absolute_error, 2
            ),
            "percent_error": round(
                percent_error, 2
            )
        }