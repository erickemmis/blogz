import hashlib
import random 
import string

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def make_hash_pwd(password, salt=None):
    if salt == None:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password + salt)).hexdigest()
    return '{0},{1}'.format(hash,salt)

def compare_hash(password, hash):
    salt = hash.split(',')[1]

    if make_hash_pwd(password,salt) == hash:
        return True
    return False




