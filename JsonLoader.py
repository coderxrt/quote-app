import json
import os

#save json file:
def save_json(obj ,filename):
	try:
		with open(filename,"w") as f:
			return json.dump(obj,f)
	except Exception as e:
		return f"{e}"
		
#load file
def load_json(filename):
	if not os.path.exists(filename):
		return
	else:
		with open(filename,"r") as f:
			return json.load(f)
		
##made with love 'Duke'