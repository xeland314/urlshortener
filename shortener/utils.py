from random import choice
from string import ascii_letters, digits

SIZE = 7
AVAILABLE_CHARS = ascii_letters + digits

def create_random_code(size=SIZE, chars=AVAILABLE_CHARS):
    return ''.join([choice(chars) for _ in range(size)])

def create_shortened_url(model_instance, prefix=''):
    random_code = create_random_code()
    short_url = prefix + random_code
    model_class = model_instance.__class__
    if model_class.objects.filter(short_url=short_url).exists():
        return create_shortened_url(model_instance, prefix)
    return short_url
