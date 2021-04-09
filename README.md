# Bahasa Rest API
API untuk mendapatkan kata Bahasa Indonesia secara acak

## Install
    
    pip3 install -r requiremetns.txt

## Example Request
- /check-words - (**POST**)<br/>
    **Request body**:

        {
            "word": "hari"
        }

    **Response body**:
    
        {
            "status": true,
            "message": "Kalimat terdapat pada Database"
        }

- /words-by-length - (**POST**)<br/>
    **Request body** :     

        {
            "length": 15,
            "max": 1000,
            "random": true
        }

    length : length of word<br/>
    max    : max word list<br/>
    random : Unordered words<br/>
    
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