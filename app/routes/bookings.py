from flask_restful import Resource


class BookingListResource(Resource):
    def post(self):
        # validate payload with BookingCreateSchema,
        # create BookingRequest row, call payment_service, return 201.
        return {"message": "Not implemented yet"}, 501