import json
from api import ApiKataDasar
from config import *
from bottle import request
from bottle import run, post

api = ApiKataDasar()


@post('/check-words')
def check_words():
    result = bodyValidation()

    if (result['status']):
        isValid = dataValidation({'word': str}, result['data'])

        if (isValid['status']):
            data = result['data']
            return api.check_words(data['word'])

        else:
            return isValid
    else:
        return result


@post('/words-by-length')
def check_words():
    result = bodyValidation()

    if (result['status']):
        isValid = dataValidation(
            {
                'length': int,
                'max': int,
                'random': bool
            },
            result['data']
        )

        if (isValid['status']):
            data = result['data']
            
            if (data['max'] > 101):
                return {
                    'status': False,
                    'message': "Parameter 'max' must be less than 100",
                }

            return api.get_words_with_length(data['length'], data['max'], data['random'])

        else:
            return isValid
    else:
        return result


def bodyValidation():
    try:
        postData = json.loads(request.body.read())
        return {
            'status': True,
            'data': postData
        }
    except ValueError as e:
        return {
            'status': False,
            'message': "Make sure the json format is valid",
            'error': "{}".format(e)
        }


def dataValidation(needs: dict, values: dict):
    result = {
        'status': True,
        'message': "All requirment filled"
    }

    for key, value in needs.items():
        if key not in values:
            result = {
                'status': False,
                'message': "Parameters '{}' cannot be empty".format(value)
            }
        else:
            if type(values[key]) is not value:
                result = {
                    'status': False,
                    'message': "Parameters '{}' must be {}".format(key, value)
                }

    return result


if __name__ == '__main__':
    run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
