# Bahasa Rest API
API untuk mendapatkan kata Bahasa Indonesia

## Example Request
- /check-words - (**POST**)
    **Request body**:

        {
            "word": "hari"
        }

    **Response body**:
    
        {
            "status": true,
            "message": "Kalimat terdapat pada Database"
        }

- /words-by-length - (**POST**)
    **Request body** :     

        {
            "length": 15,
            "max": 1000,
            "random": true
        }

    length : length of word
    max    : max word list
    random : Unordered words
    
    **Response body**:
    
        {
            "status": true,
            "data": [
                {
                    "kata": "psikofarmakologi",
                    "jenis_kata": "Nomina"
                },
                ...
                ...
                {
                    "kata": "yakjuj wa makjuj",
                    "jenis_kata": "Nomina"
                }
            ]
        }