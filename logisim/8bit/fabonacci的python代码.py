var0 = 0
var1 = 1
var6 = 1
var7 = 1
var8 = 0
var11 = 0
var12 = 10
while True:
	var8 = var6 + var7
	var6 = var7 + var0
	var7 = var8 + var0
	var11 = var11 + var1
	if var11 >= var12:
		break
print(var7)