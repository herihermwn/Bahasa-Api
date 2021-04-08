from database.main import KataDasarDb, KataDasar


class ApiKataDasar():

    def __init__(self):
        self.db = KataDasarDb()

    def check_words(self, word):
        words = self.db.get_item_by_column(value= word, column=KataDasar.kata)
        
        if (words == None):
            return {
                'status': False,
                'message': "Kalimat belum ada pada Database"
            }
        else:
            return {
                'status': True,
                'message': "Kalimat terdapat pada Database"
            }
            

    def get_words_with_length(self, length, max, random=False):
        if (random):
            words = self.db.get_random_words_by_length(length, max)
        else:
            words = self.db.get_words_by_length(length, max)

        if (words == None):
            return {
                'status': False,
                'data': []
            }
        else:
            listWords = []
            for w in words:
                listWords.append({
                    "kata": w.kata,
                    "jenis_kata": w.tipe,
                })

            return {
                'status': True,
                'data': listWords
            }
            