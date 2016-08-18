#MvI_BatchEdit.py

from Tkinter import *
from tkFileDialog import askopenfilename
import os, subprocess, re, htmlentitydefs, inspect, sys, platform
from time import sleep, strftime

print """
 ______      _____    ______                  _        _______    _ _      
|  ___ \    (_____)  (____  \       _        | |      (_______)  | (_)_    
| | _ | |_   _ _  1.1 ____)  ) ____| |_  ____| | _     _____   _ | |_| |_  
| || || | | | | |    |  __  ( / _  |  _)/ ___) || \   |  ___) / || | |  _) 
| || || |\ V /| |_   | |__)  | ( | | |_( (___| | | |  | |____( (_| | | |__ 
|_||_||_| \_(_____)  |______/ \_||_|\___)____)_| |_|  |_______)____|_|\___)
                                                                           
	**** UC Libraries Record Loads Working Group ****
"""

class utilityFunctions:

	def BrowseFiles(self):#open file explorer
		root=Tk()
		root.withdraw()
		filename = askopenfilename(filetypes=[("MARC files","*.mrc"),("XML files","*.xml"),("All the files","*.*")], title="R.L.W.G Batch Edit -- select input file")
		print '\n\nSelected file: \"' + re.sub('.*/(.*?)$', '\\1\"', filename) + '\n'
		root.destroy()
		return filename

	def listChangeScripts(self, BatchEdits):
		
		num = 0
		ChangeScriptsDict = {}
		for i in dir(BatchEdits)[:-2]:
			num = num + 1
			ChangeScriptsDict[num] = [i, ''.join(inspect.getargspec(getattr(BatchEdits, i))[3])]
		for key in ChangeScriptsDict.keys():
			print key, ': ' + ChangeScriptsDict[key][1]
		return ChangeScriptsDict

	def ScriptSelect(self):#options list
		NumberOfOptions = len(ChangeScriptsDict)
		def ScriptSelectValidate(low, high):
			prompt = '\nSelect number for desired process: '
			while True:
				try:
					a = int(raw_input(prompt))
					if low <= a <= high:
						return a
					else:
						print('\nPlease select a number between %d and %d!\a ' % (low, high))
				except ValueError:
					print('\nPlease select a number between %d and %d!\a ' % (low, high))
			return
		x = ScriptSelectValidate(1, NumberOfOptions)
		verify = raw_input('\nYou have selected:\n\n\t ' + ChangeScriptsDict[x][1] + '\n\nConfirm (y/n): ')
		while verify != 'y':
			while verify != 'y' and verify != 'n':
				verify = raw_input('Please type \'y\' or \'n\'')
			if verify == 'y':
				pass
			else:
				x = ScriptSelectValidate(1, NumberOfOptions)
				verify = raw_input('\nYou have selected:\n\n\t' + str(x) + '. ' + ChangeScriptsDict[x][1] + '\n\nConfirm (y/n): ')
		return x

	def MarcEditBreakFile(self, x):
		#break the file; output .mrk
		print x
		mrkFileName = re.sub('.mrc', '.mrk', x)
		print "\n<Breaking MARC file>\n"
		subprocess.call(['C:\\%s\\MarcEdit 6\\cmarcedit.exe' % MarcEditDir, '-s', x, '-d', mrkFileName, '-break'])
		x = open(mrkFileName).read()
		return x

	def MarcEditBreakFileTranslateToMarc8(self, x):
		#break the file; output .mrk
		print x
		mrkFileName = re.sub('.mrc', '.mrk', x)
		print "\n<Breaking MARC file>\n"
		subprocess.call(['C:\\%s\\MarcEdit 6\\cmarcedit.exe' % MarcEditDir, '-s', x, '-d', mrkFileName, '-break', '-marc8'])
		x = open(mrkFileName).read()
		return x

	def MarcEditMakeFile(self, x):
		print '\n<Compiling file to MARC>\n'
		subprocess.call(['C:\\%s\\MarcEdit 6\\cmarcedit.exe' % MarcEditDir, '-s', filenameNoExt + '_OUT.mrk', '-d', filenameNoExt + '_OUT.mrc', '-make'])
		return x

	def MarcEditSaveToMRK(self, x):
		outfile = open(filenameNoExt + '_OUT.mrk', 'w')
		outfile.write(x)
		outfile.close()
		return

	def Standardize856_956z(self, x):
		output = []
		#Check 8/956 indicator 1 code for non http URL
		URLFieldInd1 = re.findall('=[8|9]56  [^4]..*', x)
		#if found, interrupt script with alert
		if URLFieldInd1:
			print '\a\a\nFound URL fields(s) with unexpected indicator:\n'
			for URLField in URLFieldInd1:
				print '\t' + URLField
			raw_input('\nPress <ENTER> to continue\n')
		#split file into list of lines
		x = x.split('\n')
		for line in x:
			match = re.search('=[8|9]56  ..', line)
			if match:
				#delete all occurance of $2
				line = re.sub('\$2http[^\$]*', '', line)
				#delete all $z
				line = re.sub('\$z[^\$]*', '', line)
				#delete all occurance of $q
				line = re.sub('\$q[^\$]*', '', line)
				#delete all occurance of $y
				line = re.sub('\$y[^\$]*', '', line)
				#move leading $3 to EOF
				line = re.sub('(=[8|9]56  ..)(\$3.*?)(\$u.*)', '\\1\\3\\2', line)
				#add standard $z
				line = line + '$zConnect to resource online'
				output.append(line)
			else:
				output.append(line)
		x = '\n'.join(output)
		return x
	
	def AddEresourceGMD(self, x):
		record = x
		if re.search('=245.*\$h', record) == None:
			print record
			if re.search('=245.*\$b', record):
				record = re.sub('(=245.*)(\s:\$b.*)', '\\1$h[electronic resource]\\2', record)
				print record
			elif re.search('=245.*\$c', record):
				record = re.sub('(=245.*)(/\$c.*)', '\\1$h[electronic resource] \\2', record)
			else:
				record = re.sub('(=245.*)\.?', '\\1$h[electronic resource]', record)
		x = record
		return x
	
	def CharRefTrans(self, x):#Character reference translation table
		CharRefTransTable = {
			#Hex char refs
			'&#039;' : ['&#039;', '\"'],
			'&#160;' : ['&#160;', '  '],
			'&#160;' : ['&#160;', '{A0}'],
			'&#161;' : ['&#161;', '{iexcl}'],
			'&#163;' : ['&#163;', '{pound}'],
			'&#168;' : ['&#168;', '{uml}'],
			'&#169;' : ['&#169;', '{copy}'],
			'&#174;' : ['&#174;', '{reg}'],
			'&#176;' : ['&#176;', '{deg}'],
			'&#177;' : ['&#177;', '{plusmin}'],
			'&#181;' : ['&#181;', '[micro]'],
			'&#192;' : ['&#192;', '{grave}A'],
			'&#193;' : ['&#193;', '{acute}A'],
			'&#194;' : ['&#194;', '{circ}A'],
			'&#195;' : ['&#195;', '{tilde}A'],
			'&#196;' : ['&#196;', '{uml}A'],
			'&#197;' : ['&#197;', '{ring}A'],
			'&#198;' : ['&#198;', '{AElig}'],
			'&#199;' : ['&#199;', '{cedil}C'],
			'&#200;' : ['&#200;', '{grave}E'],
			'&#201;' : ['&#201;', '{acute}E'],
			'&#202;' : ['&#202;', '{circ}E'],
			'&#203;' : ['&#203;', '{uml}E'],
			'&#204;' : ['&#204;', '{grave}I'],
			'&#205;' : ['&#205;', '{acute}I'],
			'&#206;' : ['&#206;', '{circ}I'],
			'&#207;' : ['&#207;', '{uml}I'],
			'&#209;' : ['&#209;', '{tilde}N'],
			'&#210;' : ['&#210;', '{grave}O'],
			'&#211;' : ['&#211;', '{acute}O'],
			'&#212;' : ['&#212;', '{circ}O'],
			'&#213;' : ['&#213;', '{tilde}O'],
			'&#214;' : ['&#214;', '{uml}O'],
			'&#217;' : ['&#217;', '{grave}U'],
			'&#218;' : ['&#218;', '{acute}U'],
			'&#219;' : ['&#219;', '{circ}U'],
			'&#220;' : ['&#220;', '{uml}U'],
			'&#221;' : ['&#221;', '{acute}Y'],
			'&#222;' : ['&#222;', '{THORN}'],
			'&#224;' : ['&#224;', '{grave}a'],
			'&#225;' : ['&#225;', '{acute}a'],
			'&#226;' : ['&#226;', '{circ}a'],
			'&#227;' : ['&#227;', '{tilde}a'],
			'&#228;' : ['&#228;', '{uml}a'],
			'&#229;' : ['&#229;', '{ring}a'],
			'&#230;' : ['&#230;', '{aelig}'],
			'&#231;' : ['&#231;', '{cedil}c'],
			'&#232;' : ['&#232;', '{grave}e'],
			'&#233;' : ['&#233;', '{acute}e'],
			'&#234;' : ['&#234;', '{circ}e'],
			'&#235;' : ['&#235;', '{uml}e'],
			'&#236;' : ['&#236;', '{grave}i'],
			'&#237;' : ['&#237;', '{acute}i'],
			'&#238;' : ['&#238;', '{circ}i'],
			'&#239;' : ['&#239;', '{uml}i'],
			'&#240;' : ['&#240;', '{eth}'],
			'&#241;' : ['&#241;', '{tilde}n'],
			'&#242;' : ['&#242;', '{grave}o'],
			'&#243;' : ['&#243;', '{acute}o'],
			'&#244;' : ['&#244;', '{circ}o'],
			'&#245;' : ['&#245;', '{tilde}o'],
			'&#246;' : ['&#246;', '{uml}o'],
			'&#249;' : ['&#249;', '{grave}u'],
			'&#250;' : ['&#250;', '{acute}u'],
			'&#251;' : ['&#251;', '{circ}u'],
			'&#252;' : ['&#252;', '{uml}u'],
			'&#253;' : ['&#253;', '{acute}y'],
			'&#254;' : ['&#254;', '{thorn}'],
			'&#255;' : ['&#255;', '{uml}y'],
			'&#34;' : ['&#34;', '\"'],
			'&#38;' : ['&#38;', '&'],
			'&#39;' : ['&#39;', '\''],
			'&#60;' : ['&#60;', '<'],
			'&#62;' : ['&#62;', '>'],
			'&#8195;' : ['&#8195;', '  '],
			'&#8209;' : ['&#8209;', '-', '-'],
			'&#8211;' : ['&#8211;', '-'],
			'&#8212;' : ['&#8212;', '--'],
			'&#8213;' : ['&#8213;', '--'],
			'&#8216;' : ['&#8216;', '\''],
			'&#8217;' : ['&#8217;', '\''],
			'&#8220;' : ['&#8220;', '\"'],
			'&#8221;' : ['&#8221;', '\"'],
			'&#8223;' : ['&#8223;', '\"', '\"'],
			'&#8226;' : ['&#8226;', '{middot}'],
			'&#8482;' : ['&#8482;', '[TM]'],
			'&#8804;' : ['&#8804;', '<=', '<='], 
			'&#8805;' : ['&#8805;', '>=', '>='],
			'&#913;' : ['&#913;', '[Alpha]'],
			'&#914;' : ['&#914;', '[Beta]'],
			'&#915;' : ['&#915;', '[Gamma]'],
			'&#916;' : ['&#916;', '[Delta]'],
			'&#917;' : ['&#917;', '[Epsilon]'],
			'&#918;' : ['&#918;', '[Zeta]'],
			'&#919;' : ['&#919;', '[Eta]'],
			'&#920;' : ['&#920;', '[Theta]'],
			'&#921;' : ['&#921;', '[Iota]'],
			'&#922;' : ['&#922;', '[Kappa]'],
			'&#923;' : ['&#923;', '[Lambda]'],
			'&#924;' : ['&#924;', '[Mu]'],
			'&#925;' : ['&#925;', '[Nu]'],
			'&#926;' : ['&#926;', '[Xi]'],
			'&#927;' : ['&#927;', '[Omicron]'],
			'&#928;' : ['&#928;', '[Pi]'],
			'&#929;' : ['&#929;', '[Rho]'],
			'&#931;' : ['&#931;', '[Sigma]'],
			'&#932;' : ['&#932;', '[Tau]'],
			'&#933;' : ['&#933;', '[Upsilon]'],
			'&#934;' : ['&#934;', '[Phi]'],
			'&#935;' : ['&#935;', '[Chi]'],
			'&#936;' : ['&#936;', '[Psi]'],
			'&#937;' : ['&#937;', '[Omega]'],
			'&#945;' : ['&#945;', '[alpha]'],
			'&#946;' : ['&#946;', '[beta]'],
			'&#947;' : ['&#947;', '[gamma]'],
			'&#948;' : ['&#948;', '[delta]'],
			'&#949;' : ['&#949;', '[epsilon]'],
			'&#950;' : ['&#950;', '[zeta]'],
			'&#951;' : ['&#951;', '[eta]'],
			'&#952;' : ['&#952;', '[theta]'],
			'&#953;' : ['&#953;', '[iota]'],
			'&#954;' : ['&#954;', '[kappa]'],
			'&#955;' : ['&#955;', '[lambda]'],
			'&#956;' : ['&#956;', '[mu]'],
			'&#957;' : ['&#957;', '[nu]'],
			'&#958;' : ['&#958;', '[xi]'],
			'&#959;' : ['&#959;', '[omicron]'],
			'&#960;' : ['&#960;', '[pi]'],
			'&#961;' : ['&#961;', '[rho]'],
			'&#963;' : ['&#963;', '[sigma]'],
			'&#964;' : ['&#964;', '[tau]'],
			'&#965;' : ['&#965;', '[upsilon]'],
			'&#966;' : ['&#966;', '[phi]'],
			'&#967;' : ['&#967;', '[chi]'],
			'&#968;' : ['&#968;', '[psi]'],
			'&#969;' : ['&#969;', '[omega]'],
			'&#x0027;' : ['&#x0027;', '\''],
			'&#x0101;' : ['&#x0101;', '{macr}a', '{229}a'],
			'&#x142;' : ['&#x142;', '{lstrok}', '{177}'],
			'&#x153;' : ['&#x153;', '{oelig}', '{182}'],
			'&#x2013;' : ['&#x2013;', '-'],
			'&#x2014;' : ['&#x2014;', '--'],
			'&#x2018;' : ['&#x2018;', '\''],
			'&#x2019;' : ['&#x2019;', '\''],
			'&#x201E;' : ['&#x201E;', '\"', '\"'],
			'&#x2022;' : ['&#x2022;', ''],
			'&#x2022;' : ['&#x2022;', '{middot}', '{168}'],
			'&#x2039;' : ['&#x2039;', '\'', '\''],
			'&#x203A;' : ['&#x203A;', '\'', '\''],
			'&#x2b9;' : ['&#x2b9;', '\'', '\''],
			'&#x2bb;' : ['&#x2bb;', '\'', '\''],
			'&#x2bb;' : ['&#x2bc;', '\'', '\''],
			'&#x300;' : ['&#x300;', '{grave}', '{225}'],
			'&#x301;' : ['&#x301;', '{acute}', '{226}'],
			'&#x302;' : ['&#x302;', '{circ}', '{227}'],
			'&#x303;' : ['&#x303;', '{tilde}', '{228}'],
			'&#x304;' : ['&#x304;', '{macr}', '{229}'],
			'&#x306;' : ['&#x306;', '{breve}', '{230}'],
			'&#x307;' : ['&#x307;', '{dot}', '{231}'],
			'&#x308;' : ['&#x308;', '{uml}', '{232}'],
			'&#x30c;' : ['&#x30c;', '{caron}', '{233}'],
			'&#x323;' : ['&#x323;', '{dotb}', '{242}'],
			'&#x326;' : ['&#x326;', '{commab}', ','],
			'&#x327;' : ['&#x327;', '{cedil}', '{240}'],
			'&#x328;' : ['&#x328;', '{ogon}', '{241}'],
			'&#x81;' : ['&#x81;', '', ''],#control char
			'&#xA6;' : ['&#xA6;', '[broken bar]', '[broken bar]'],
			'&#xe6;' : ['&#xe6;', '{aelig}', '{181}'],
			'&#xfe20;' : ['&#xfe20;', '{llig}', '{235}'],
			'&#xfe21;' : ['&#xfe21;', '{rlig}', '{236}'],
			'&Delta;' : ['&Delta;', '[Delta]', '[Delta]'],
			'&Lambda;' : ['&Lambda;', '[Lambda]', '[Lambda]'],
			'&Prime;' : ['&Prime;', '\'', '\''],
			'&aacute;' : ['&aacute;', '{acute}a', '{226}a'],
			'&acirc;' : ['&acirc;', '{circ}a', '{227}a'],
			'&acute;' : ['&acute;', '{acute}', '{226}'],
			'&aelig;' : ['&aelig;', '{aelig}', '{181}'],
			'&agr;' : ['&agr;', '[alpha]', '[alpha]'],
			'&alpha;' : ['&alpha;', '[alpha]', '[alpha]'],
			'&amp;' : ['&amp;', '&', '&'],
			'&ap;' : ['&ap;', '[almost equal to]', '[almost equal to]'],
			'&aring;' : ['&aring;', '{ring}a', '{234}a'],
			'&Aring;' : ['&Aring;', '{ring}A', '{234}A'],
			'&ast;' : ['&ast;', '*', '*'],
			'&auml;' : ['&auml;', '{uml}', '{232}'],
			'&bull;' : ['&bull;', '{middot}', '{168}'],
			'&cacute;' : ['&cacute;', '{acute}c', '{226}c'],
			'&ccaron;' : ['&ccaron;', '{caron}', '{233}'],
			'&ccedil;' : ['&ccedil;', '{cedil}c', '{240}c'],
			'&circ;' : ['&circ;', '{circ}', '{227}'],
			'&dashv;' : ['&dashv;', '[left tack]', '[left tack]'],
			'&dollar;' : ['&dollar;', '{dollar}', '$'],
			'&deg;' : ['&deg;', '{deg)', '{234}'],
			'&delta;' : ['&delta;', '[delta]', '[delta]'],
			'&eacute;' : ['&eacute;', '{acute}e', '{226}e'],
			'&egr;' : ['&egr;', '[epsilon]', '[epsilon]'],
			'&Egr;' : ['&Egr;', '[Epsilon]', '[Epsilon]'],
			'&esc;' : ['&esc;', '', ''],
			'&ge;' : ['&ge;', '>=', '>='],
			'&grave;' : ['&grave;', '{grave}', '{225}'],
			'&gt;' : ['&gt;', '>', '>'],
			'&hacek;' : ['&hacek;', '{caron}', '{233}'],
			'&hardsign;' : ['&hardsign;', '{hardsign}', '{183}'],
			'&iacute;' : ['&iacute;', '{acute}i', '{226}'],
			'&iexcl;' : ['&iexcl;', '{iexcl}', '{160}'],
			'&inches;' : ['&inches;', '\"', '\"'],
			'&kappa;' : ['&kappa;', '[kappa]', '[kappa]'],
			'&Lambda;' : ['&Lambda', '[Lambda]', '[Lambda]'],
			'&le;' : ['&le;', '<=', '<='],
			'&lt;' : ['&lt;', '<', '<'],
			'&macr;' : ['&macr;', '{macr}', '{macr}'],
			'&mdash;' : ['&mdash;', '--', '--'],
			'&mgr;' : ['&mgr;', '[Mu]', '[Mu]'],
			'&middot;' : ['&middot;', '{middot}', '{168}'],
			'&mllhring;' : ['&mllhring;', '{mlrhring}', '{174}'],
			'&mlrfring;' : ['&mlrfring;', '{mlrfring}', '{176}'],
			'&mu;' : ['&mu;', '[mu]', '[mu]'],
			'&nacute;' : ['&nacute;', '{acute}n', '{226}n'],
			'&nbsp;' : ['&nbsp;', ' ', ' '],
			'&ndash;' : ['&ndash;', '-', '-'],
			'&ne;' : ['&ne;', '[not equal]', '[not equal]'],
			'&ntilde;' : ['&ntilde;', '{tilde}n', '{228}n'],
			'&Ntilde;' : ['&Ntilde;', '{tilde}N', '{228}N'],
			'&oacute;' : ['&oacute;', '{acute}o', '{226}o'],
			'&ocirc;' : ['&ocirc;', '{circ}o', '{227}o'],
			'&oslash;' : ['&oslash;', '{Ostrok}', '{162}'],
			'&ouml;' : ['&ouml;', '{uml}o', '{232}o'],
			'&Ouml;' : ['&Ouml;', '{uml}O', '{232}O'],
			'&perp;' : ['&perp;', '[up tack]', '[up tack]'],
			'&phis;' : ['&phis;', '[phi]', '[phi]'],
			'&phiv;' : ['&phiv;', '[Phi]', '[Phi]'],
			'&pi;' : ['&pi;', '[pi]', '[pi]'],
			'&quot;' : ['&quot;', '\"', '\"'],
			'&radic;' : ['&radic;', '[check mark]', '[check mark]'],
			'&reg;' : ['&reg;', ' {reg}', '{170}'],
			'&ring;' : ['&ring;', '{ring}', '{234}'],
			'&scedil;' : ['&scedil;', '{cedil}s', '{240}s'],
			'&sect;' : ['&sect;', '[section]', '[section]'],
			'&shy' : ['&shy', '-', '-'],
			'&shy;' : ['&shy;', '-', '-'],
			'&sigma;' : ['&sigma;', '[sigma]', '[sigma]'],
			'&sim;' : ['&sim;', '[equivalent]', '[equivalent]'],
			'&softsign;' : ['&softsign;', '{softsign}', '{167}'],
			'&sol;' : ['&sol;', '/', '/'],
			'&square;' : ['&square;', '[square]', '{175}'],
			'&szlig;' : ['&szlig;', 'ss', 'ss'],
			'&thgr;' : ['&thgr;', '[theta]', '[theta]'],
			'&thinsp;' : ['&thinsp;', ' ', ' '],
			'&trade;' : ['&trade;', '[TM]', '[TM]'],
			'&uuml;' : ['&uuml;', '{uml}u', '{232}u'],
			'&zcaron;' : ['&zcaron;', '{caron}z', '{233}z'],
			}
		
		keys = dict.keys(CharRefTransTable)
		for key in range(len(keys)):
			x = re.sub(CharRefTransTable[keys[key]][0], CharRefTransTable[keys[key]][1], x)
		#Flag unknown Char Refs
		UnrecognizedCharRef = list(set(re.findall('&[\d|\w]*;', x)))
		if UnrecognizedCharRef:
			BoolUnrecognizedCharRef = 1
			CharRefIf = open(filename + '_UnrecognizedCharRef.txt', 'w')
			CharRefIf.write('Unrecognized character references\n')
			CharRefIf.write('\n'.join(UnrecognizedCharRef))
			CharRefIf.close()
		return x
	
	def DeleteLocGov(self, x):
		x = re.sub('(?m)^=856.*www.loc.gov.*\n', '', x)
		x = re.sub('(?m)^=856.*www.e-streams.com.*\n', '', x)
		x = re.sub('(?m)^=856.*Book review (E-STREAMS).*\n', '', x)
		x = re.sub('(?m)^=856.*catdir.loc.gov.*\n', '', x)
		x = re.sub('(?m)^=856.*books.google.com.*\n', '', x)
		x = re.sub('(?m)^=856.*cover image.*\n', '', x)
		x = re.sub('(?m)^=856.*http://d-nb.info.*\n', '', x)
		x = re.sub('(?m)^=856.*http://deposit.d-nb.de/cgi-bin.*\n', '', x)
		return x

class batchEdits:

	def MvIShipLists(self, x, name='MvI Shiplists'):
		def MvICheckForFull(x):
			#split string into list of strings for individual records
			x = x.split('\n\n')
			ShipListRecs = []
			FullRecs = []
			for record in x:
				if re.search('=001  gp', record):
					FullRecs.append(record)
				else:
					ShipListRecs.append(record)
			if len(FullRecs) > 0:
				print '\a\a\a\nFull Records found, generating error file \'' + strftime("%Y%m%d") + 'FullMarcRecord.mrk\'\n'
				FullRecsMrk = '\n\n'.join(FullRecs)
				file = open(strftime("%Y%m%d") + 'SendToJeff.mrk', 'w')
				file.write(FullRecsMrk)
				file.close()
			x = '\n\n'.join(ShipListRecs)
			return x
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Check for Full catalog records and seperate from file if present
		x = MvICheckForFull(x)
		#move 001 to 002
		x = re.sub('=001  tmp', '=002  XM tmp', x)
		#replace 913 with 949 stem
		x = re.sub('=913.*TEMPORARY RECORD ', r'=949  \\1$a', x)
		#add elements to 949 and append 049 control field
		x = re.sub('(=949.*)', '\\1$lulagy$rz$z086\n=049  \\\\\$aCINN', x)
		#move shiplist date to 997
		x = re.sub('=500.*\$aShipping list date ', '=997  \\\\\$a', x)
		#move shiplist note to 996
		x = re.sub('=500.*\$aShipping list ', '=996  \\\\\$a', x)
		x = utilities.MarcEditMakeFile(utilities.MarcEditSaveToMRK(utilities.CharRefTrans(utilities.DeleteLocGov(x))))
		return x
	
	def MvIFull(self, x, name='MvI Full'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		def MvIEresource(x):
			#add elements to 949 and append 049 control field
			x = re.sub('(=949.*)', '\\1$luint$t99$rs$z086\n=949  \\\\\$a*bn=buint', x)
			x = utilities.AddEresourceGMD(x)
			return x
		
		def MvIPrint(x):
			#add command fields to create print format item and set bib location to bula
			x = re.sub('(=949.*)', '\\1$lulagy$t01$z086\n=949  \\\\\$a*bn=bula;', x)
			#search for presense of 856, if present, add command field to create online format item
			if re.search('=856', x):
				x = re.sub('(=949.*)(\$lulagy.*)', '\\1\\2\n\\1$luint$t99$rs$z086', x)
				#if 856 present, check for 007, add if missing
				match007 = re.search('=007', x)
				if match007:
					pass
				else:
					x = re.sub('=245', '=007  cr|mnu\n=245', x)
			return x
		
		#Global changes for MvI full records
		#move 001 to 035
		x = re.sub('=001  gp', r'=035  \\\\$a(GPO)', x)
		#replace 913 with 949 stem
		x = re.sub('=913.*\$c', r'=949  \\1$a', x)
		#move 035 OCLC no to 001
		x = re.sub('=035  \\\\0\$aoc', '=001  oc', x)
		#delete 599 and 999 fields
		x = re.sub('=599.*\n', '', x)
		x = re.sub('=999.*\n', '', x)
		#standardize 856 if present
		x = re.sub('(=856.*?)\$u', '\\1$zConnect to resource online$u', x)
		x = re.sub('=856  7.', '=856  40', x)
		# Remove "$2hhtp" wherever it appears
		x = re.sub('\$2hhtp', '', x)
		
		
		#split string into list of strings for individual records
		x = x.split('\n\n')
		#create empty lists for sorting categories of records
		MvIEresourceList = []
		MvIPrintList = []
		#loop over each record and add to category based on presence of electronic GMD field
		for record in x:
			#check MvIFullList for 040MvI; add where missing
			match040 = re.search('=040.*MvI', record)
			if match040:
				pass 
			else:
				record = re.sub('(=040.*)', '\\1$dMvI', record)
			#check for presence of GMD [electronic resource] or RDA 338 online resource, sort based on such
			if re.search('\$h\[elect', record) or re.search('=338.*online', record):
				MvIEresourceList.append(MvIEresource(record))
			else:
				MvIPrintList.append(MvIPrint(record))
	
		#join lists back into one string for each category and apply change script
		MvIEresourceList = '\n\n'.join(MvIEresourceList)
		MvIPrintList = '\n\n'.join(MvIPrintList)
		#join categories back into one file
		if len(MvIEresourceList) > 0 and len(MvIPrintList) > 0:
			MvIEresourceList = MvIEresourceList + '\n\n'
		x = MvIEresourceList + MvIPrintList
		x = utilities.MarcEditMakeFile(utilities.MarcEditSaveToMRK(utilities.CharRefTrans(utilities.DeleteLocGov(x))))
		return x

	def MvIFullMicrofiche(self, x, name='MvI FullMicrofiche'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		def add949fields(x):
			#add command fields to create print format item and set bib location to bula
			x = re.sub('(=949.*)', '\\1$lulamg$t60$z086\n=949  \\\\\$a*bn=bula;', x)
			#search for presense of 856, if present, add command field to create online format item
			if re.search('=856', x):
				x = re.sub('(=949.*)(\$lulamg.*)', '\\1\\2\n\\1$luint$t99$rs$z086', x)
				#if 856 present, check for 007, add if missing
				match007 = re.search('=007', x)
				if match007:
					pass
				else:
					x = re.sub('=245', '=007  cr|mnu\n=245', x)
			return x
		#Global changes for MvI full records
		#move 001 to 035
		x = re.sub('=001  gp', r'=035  \\\\$a(GPO)', x)
		#replace 913 with 949 stem
		x = re.sub('=913.*\$c', r'=949  \\1$a', x)
		#move 035 OCLC no to 001
		x = re.sub('=035  \\\\0\$aoc', '=001  oc', x)
		#delete 599 and 999 fields
		x = re.sub('=599.*\n', '', x)
		x = re.sub('=999.*\n', '', x)
		#standardize 856 if present
		x = re.sub('(=856.*?)\$u', '\\1$zConnect to resource online$u', x)
		x = re.sub('=856  7.', '=856  40', x)
		# Remove "$2hhtp" wherever it appears
		x = re.sub('\$2hhtp', '', x)
		x = x.split('\n\n')
		#loop over each record and look for 040 MvI
		Has040 = []
		for record in x:
			#check MvIFullList for 040MvI; add where missing
			match040 = re.search('=040.*MvI', record)
			if match040:
				pass 
			else:
				record = re.sub('(=040.*)', '\\1$dMvI', record)
			Has040.append(record)
		x = add949fields('\n\n'.join(Has040))
		x = utilities.MarcEditMakeFile(utilities.MarcEditSaveToMRK(utilities.CharRefTrans(utilities.DeleteLocGov(x))))
		return x

	
	
	#Instantiate classes
BatchEdits = batchEdits()
utilities = utilityFunctions()

#get bit environment
global MarcEditDir
platformbit = platform.architecture()[0]
if platformbit == '32bit':
	MarcEditDir = 'Program Files'
elif platformbit == '64bit':
	MarcEditDir = 'Program Files'
		
#browse to input file and open
filename = utilities.BrowseFiles()

#get filename and strip extension
filenameNoExt = re.sub('.\w*$', '', filename)

#create dictionary/menu of all available change scripts
ChangeScriptsDict = utilities.listChangeScripts(BatchEdits)

#select change script by index in dictionary
SelectedProcess = utilities.ScriptSelect()
methodToCall = getattr(BatchEdits, ChangeScriptsDict[int(SelectedProcess)][0])
result = methodToCall(filename)


raw_input('\nOutput File...\n\n\t\tEditing finished, press <ENTER> to exit\n\n\n')
