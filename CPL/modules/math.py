import _random



r_i=_random.Random()



def _random(params):
	return r_i.random()



def _min(params):
	v=None
	for p in params:
		if (v==None):
			v=p.value
		else:
			v=min(v,p.value)
	return v



def _max(params):
	v=None
	for p in params:
		if (v==None):
			v=p.value
		else:
			v=max(v,p.value)
	return v



def _floor(params):
	return int(str(params[0].value).split(".")[0])



def _ceil(params):
	return int(str(params[0].value).split(".")[0])+1



def _round(params):
	return round(params[0].value)



def _abs(params):
	return abs(params[0].value)



def _sign(params):
	if (params[0].value<0):return -1
	if (params[0].value==0):return 0
	return 1



# constrain()
# dist()
# exp()
# lerp()
# log()
# mag()
# map()
# sqrt()

# acos()
# asin()
# atan()
# atan2()
# cos()
# degrees()
# radians()
# sin()
# tan()

# randomSeed()