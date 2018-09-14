import time, requests
from decimal import Decimal
from datetime import datetime as dt
from math import log

pair			=  ['BTC','USDT'] 
#pair			=  ['ADA','USDT'] 
#pair			=  ['BNB','USDT'] 
#pair			=  ['ADA','BTC'] 
#pair			=  ['NANO','BTC'] 
#pair			=  ['NANO','BNB']
#pair			=  ['ONT','USDT'] 

top				= 20

symbol_binance 	= pair[0]+pair[1]

if(pair[0] == 'BTC'): 	tpair0 = 'XBT'
else:					tpair0 = pair[0]
symbol_bitmex = tpair0

def round_num(f): 
	if(f>=1): return (9-(int(round(log(f,10),3))+1))
	else: return 8#min(abs(Decimal(str(f)).as_tuple().exponent),8)
def dround(f): return round(Decimal(f), 0)
def dround1(n): return round(Decimal(n), round_price_list[0])
def dround2(n): return round(Decimal(n), round_price_list[1])
def fround8(f): return round(float(f), 8)

binance_down	= True
bitmex_down 	= True
orderbook_binance = requests.get("https://api.binance.com/api/v1/depth?symbol="+symbol_binance+"&limit=1000").json()  
if(not 'code' in orderbook_binance.keys()): binance_down = False
orderbook_bitmex = requests.get("https://www.bitmex.com/api/v1/orderBook/L2?symbol="+symbol_bitmex+"&depth=1000").json()
if(orderbook_bitmex != []): bitmex_down = False

round_price_list 	= [0,0]
ask_plist 			= [0,0]
ask_vlist 			= [0,0]
bid_plist 			= [0,0]
bid_vlist 			= [0,0]
max_v	  			= [0,0]
ask_aplist 			= [0,0]
ask_avlist 			= [0,0]
bid_aplist 			= [0,0]
bid_avlist 			= [0,0]
sample_range		= [0,0]

#RUN THRU EXCHANGES
for w in range(0, 2):#top_ask 	= 0
	sample_price = 0
	sample_range[w] = 0

	if(w == 0 and binance_down == False): 
		temp_orderbook = orderbook_binance
		sample_price = float(temp_orderbook['bids'][0][0]) ##print("NANCE SAMPLE",sample_price)

	elif(w == 1 and bitmex_down == False):
		temp_orderbook = orderbook_bitmex
		for i in range(len(temp_orderbook)): #GO THRU ENTIRE JSON ARRAY
			if(temp_orderbook[i]['side'] == 'Buy' and sample_price == 0):
				sample_price = float(temp_orderbook[i]['price'])#print("MEX SAMPLE",sample_price)
				break
	else: break #print("break")		
	round_price_list[w] = round_num(sample_price)
	sample_range[w] = sample_price * 0.01

	#SEARCHES ORDERBOOK FOR WALLS STARTING FROM X = 0 (ASK) AND X = 1 (BID)
	for x in range(0, 2):
		temp_plist 		= [0]*top
		temp_vlist 		= [0]*top
		temp_aplist 	= []
		temp_avlist 	= []
		temp_avslist 	= []	#ACCUMULATED VALUE SCORE LIST
		temp_avsrlist 	= [0]*2
		temp_avsrpos 	= [0]*2 #if(w == 1): print("VLIST CHECK", x, temp_vlist)

		if(w == 0): #BINANCE
			if(x == 0): bids_asks = 'asks'
			else: bids_asks = 'bids'
			temp_len = len(temp_orderbook[bids_asks])
		elif(w == 1):
			temp_len = len(temp_orderbook)

		for i in range(temp_len): #GO THRU ENTIRE JSON ARRAY
			#IF BINANCE AND ASK, REVERSE ASK ORDER FROM HIGH TO LOW
			if(w == 0 and x == 0): i = (i+1)*(-1)
			accum_value = 0

			if(w == 0): #IF BINANCE
				level_price = float(temp_orderbook[bids_asks][i][0])
				level_value = float(temp_orderbook[bids_asks][i][1])*float(temp_orderbook[bids_asks][i][0]) # #accum_vlist = []	

				for j in range(i, temp_len):
					if(abs(float(temp_orderbook[bids_asks][j][0]) - level_price) > sample_range[w]/2): break #print(accum_value) #print(accum_vlist)
					else: #if(x==1):print("+",float(temp_orderbook[bids_asks][j][0]),'\t',float(temp_orderbook[bids_asks][j][1])*float(temp_orderbook[bids_asks][j][0]))
						accum_value = fround8(accum_value + float(temp_orderbook[bids_asks][j][1])*float(temp_orderbook[bids_asks][j][0])) ##accum_vlist.append(float(temp_orderbook[bids_asks][j][1])*float(temp_orderbook[bids_asks][j][0]))
				for j in range(i-1, temp_len*-1, -1):
					if(abs(float(temp_orderbook[bids_asks][j][0]) - level_price) > sample_range[w]/2): break
					else: #if(x==1):print("-",float(temp_orderbook[bids_asks][j][0]),'\t',float(temp_orderbook[bids_asks][j][1])*float(temp_orderbook[bids_asks][j][0]))
						accum_value = fround8(accum_value + float(temp_orderbook[bids_asks][j][1])*float(temp_orderbook[bids_asks][j][0])) ##accum_vlist.append(float(temp_orderbook[bids_asks][j][1])*float(temp_orderbook[bids_asks][j][0]))
			elif(w == 1): #IF BITMEX
				level_value = 0
				if(x == 0 and temp_orderbook[i]['side'] == 'Sell'):
					level_price = float(temp_orderbook[i]['price'])
					level_value = float(temp_orderbook[i]['price'])*float(temp_orderbook[i]['size'])
				if(x == 1 and temp_orderbook[i]['side'] == 'Buy'):
					level_price = float(temp_orderbook[i]['price'])
					level_value = float(temp_orderbook[i]['price'])*float(temp_orderbook[i]['size'])
				if(level_price != 0):
					for j in range(i, temp_len):
						if(abs( float(temp_orderbook[j]['price']) - level_price) > sample_range[w]/2 or (x == 0 and temp_orderbook[j]['side'] == 'Buy') or (x == 1 and temp_orderbook[j]['side'] == 'Sell')):  #print(accum_value) #print(accum_vlist) 		
							break
						else:  accum_value = fround8(accum_value + float(temp_orderbook[j]['price'])*float(temp_orderbook[j]['size']))
					for j in range(i-1, temp_len*-1, -1):
						if(abs( float(temp_orderbook[j]['price']) - level_price) > sample_range[w]/2 or (x == 0 and temp_orderbook[j]['side'] == 'Buy') or (x == 1 and temp_orderbook[j]['side'] == 'Sell')):  #print(accum_value) #print(accum_vlist) 		
							break 
						else:  accum_value = fround8(accum_value + float(temp_orderbook[j]['price'])*float(temp_orderbook[j]['size']))

			if(level_value != 0 and not (level_price < sample_price*0.33 or level_price > sample_price*3) ):
				if(level_value > min(temp_vlist)):
					for j in range(len(temp_vlist)):
						if(temp_vlist[j] == min(temp_vlist)):
							temp_plist.pop(j)
							temp_vlist.pop(j)
							temp_plist.append(level_price)
							temp_vlist.append(level_value)
							break
				if(w == 0 or (w == 1 and ((x == 0 and temp_orderbook[i]['side'] == 'Sell') or (x == 1 and temp_orderbook[i]['side'] == 'Buy') ))):
					temp_aplist.append(level_price)
					temp_avlist.append(accum_value)

		temp_avslist = [0]*len(temp_avlist)
		for i in range(1, len(temp_avslist)):
			scoreneg = 0
			scorepos = 0
			score = 0
			for j in range(i-1, -1, -1):
				if(temp_avlist[i] < temp_avlist[j]):
					scoreneg = i-j
					break
				if(j == 0): scoreneg = 999

			for j in range(i+1, len(temp_avslist)):
				if(temp_avlist[i] < temp_avlist[j]):
					scorepos = j-i
					break
				if(j == len(temp_avslist)-1): scorepos = 999
			score = min(scoreneg, scorepos)
			temp_avslist[i] = score

		for i in range(1,len(temp_avslist)-1):
			if((temp_avslist[i] > temp_avslist[i+1] and temp_avslist[i] > temp_avslist[i-1]) or (temp_avslist[i] == max(temp_avslist) and temp_avslist[i] != max(temp_avsrlist))):
				if(temp_avslist[i] > min(temp_avsrlist)):
					for j in range(len(temp_avsrlist)):
						if(temp_avsrlist[j] == min(temp_avsrlist)):
							temp_avsrlist.pop(j)
							temp_avsrlist.append(temp_avslist[i])
							temp_avsrpos.pop(j)
							temp_avsrpos.append(i)
		if(x == 0):
			ask_plist[w] = temp_plist
			ask_vlist[w] = temp_vlist

			ask_aplist[w] = [ temp_aplist[temp_avsrpos[0]], temp_aplist[temp_avsrpos[1]] ]
			ask_avlist[w] = [ temp_avlist[temp_avsrpos[0]], temp_avlist[temp_avsrpos[1]] ]
		else:
			bid_plist[w] = temp_plist
			bid_vlist[w] = temp_vlist

			bid_aplist[w] = [ temp_aplist[temp_avsrpos[0]], temp_aplist[temp_avsrpos[1]] ]
			bid_avlist[w] = [ temp_avlist[temp_avsrpos[0]], temp_avlist[temp_avsrpos[1]] ]
	
	max_v[w] = max(max(ask_avlist[w]), max(bid_avlist[w]))

print("          ",symbol_binance,dt.now())
print("             BINANCE               BITMEX")
print("                            ASKS")
for i  in range(len(ask_plist[0])):
	binance_pad 	= ""
	bitmex_pad 		= ""
	binance_dense 	= "     "
	bitmex_dense 	= ""
	for j in range(len(ask_aplist[0])):
		if(ask_plist[0][i] < ask_aplist[0][j]+sample_range[0]/2 and ask_plist[0][i] > ask_aplist[0][j]-sample_range[0]/2):
			if(int(ask_avlist[0][j]/max_v[0]*100) == 100): hundred_pad = ""
			else: hundred_pad = " "
			binance_dense = "("+str(dround(ask_avlist[0][j]/max_v[0]*100))+")"+hundred_pad	
	if(bitmex_down == False):
		for j in range(len(ask_aplist[1])):
			if(ask_plist[1][i] < ask_aplist[1][j]+sample_range[1]/2 and ask_plist[1][i] > ask_aplist[1][j]-sample_range[1]/2): bitmex_dense = "("+str(dround(ask_avlist[1][j]/max_v[1]*100))+")"
	if(dround(ask_vlist[0][i]/max_v[0]*100) < 10): binance_pad = " "
	if(binance_down == False and bitmex_down == False):
		if(dround(ask_vlist[1][i]/max_v[1]*100) < 10): bitmex_pad = " "
		print("          ",dround1(ask_plist[0][i]) ,binance_pad+str(dround(ask_vlist[0][i]/max_v[0]*100))+binance_dense,"| ",dround2(ask_plist[1][i]) ,bitmex_pad+str(dround(ask_vlist[1][i]/max_v[1]*100))+bitmex_dense )
	elif(binance_down == False and bitmex_down == True): print("          ",dround1(ask_plist[0][i]) ,binance_pad+str(dround(ask_vlist[0][i]/max_v[0]*100))+binance_dense )
print("                            BIDS")
for i  in range(len(bid_plist[0])):
	binance_pad 	= ""
	bitmex_pad 		= ""
	binance_dense 	= "     "
	bitmex_dense 	= ""
	for j in range(len(bid_aplist[0])):
		if(bid_plist[0][i] < bid_aplist[0][j]+sample_range[0]/2 and bid_plist[0][i] > bid_aplist[0][j]-sample_range[0]/2):
			if(int(bid_avlist[0][j]/max_v[0]*100) == 100): hundred_pad = ""
			else: hundred_pad = " "
			binance_dense = "("+str(dround(bid_avlist[0][j]/max_v[0]*100))+")"+hundred_pad
	if(bitmex_down == False):
		for j in range(len(bid_aplist[1])):
			if(bid_plist[1][i] < bid_aplist[1][j]+sample_range[1]/2 and bid_plist[1][i] > bid_aplist[1][j]-sample_range[1]/2): bitmex_dense = "("+str(dround(bid_avlist[1][j]/max_v[1]*100))+")"
	if(dround(bid_vlist[0][i]/max_v[0]*100) < 10): binance_pad = " "
	if(binance_down == False and bitmex_down == False): 
		if(dround(bid_vlist[1][i]/max_v[1]*100) < 10): bitmex_pad = " "
		print("          ",dround1(bid_plist[0][i]) ,binance_pad+str(dround(bid_vlist[0][i]/max_v[0]*100))+binance_dense,"| ",dround2(bid_plist[1][i]) ,bitmex_pad+str(dround(bid_vlist[1][i]/max_v[1]*100))+bitmex_dense )
	elif(binance_down == False and bitmex_down == True): print("          ",dround1(bid_plist[0][i]) ,binance_pad+str(dround(bid_vlist[0][i]/max_v[0]*100))+binance_dense )