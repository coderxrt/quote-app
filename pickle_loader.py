
import pickle
import os

def save_pickle(obj, filename):
	if not os.path.exists(filename):
		with open(filename,"wb") as f:
			return pickle.dump(obj , f)
	else:
		with open(filename,"wb") as f:
			return pickle.dump(obj , f)
		
def load_pickle(filename):
		if not os.path.exists(filename):
			return f"{filename} does not exists"
		else:
			with open(filename,"rb") as f:
				return pickle.load(f)