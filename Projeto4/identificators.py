import string
import random
from utils import * 

digitos = ''.join(random.choice(string.digits) for i in range(2))

id_client = ''.join(random.sample(digitos, len(digitos)))
id_server = ''.join(random.sample(digitos, len(digitos)))
id_arquivo = ''.join(random.sample(digitos, len(digitos)))
