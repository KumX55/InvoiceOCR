import pprint
import veryfi

client_id = "vrfa1zXdSpfZjBVfvWEXNdzOx7tbFcMb6GR6id5"
client_secret = "tmtiNcJUwklB7ISVrBVtEuuAMcdrjdB8lKn09S5BZTNs0rbk1ZMF4IuI3krDw5soBoINUZ70WwV27L8LdI6n5g6WyZ0MwekxXAa8Bk6PPWA2G4RTga4ixxM6SdBsLSju"
username = "degla996"
api_key = "66ceaa85a8f46d39e971f4b2cc19f574"

client = veryfi.Client(client_id,client_secret,username,api_key)

def prediction(facture):
    categories = ['Travel', 'Airfare', 'Lodging', 'Job supplies and materials', 'Grovery']
    json_results = client.process_document(facture,categories)
    return json_results