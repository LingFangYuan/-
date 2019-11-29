import pickle

with open('new_urls_names.txt', 'rb') as f:
    t = pickle.load(f)

print(t)

 