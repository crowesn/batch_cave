#RLWG_BatchEdit.py

from Tkinter import *
from tkFileDialog import askopenfilename
import os, subprocess, re, htmlentitydefs, inspect, sys, MARC_lang, platform
from time import sleep, strftime

print """________  ______   ___       ___________ 
___  __ \ ___  /   __ |     / /__  ____/ 
__  /_/ / __  /    __ | /| / / _  / __   
_  _, _/___  /_______ |/ |/ /__/ /_/ /__ 
/_/ |_|_(_)_____/(_)___/|__/_(_)____/_(_)  1.9
           ______        _____      ______           __________________ 
           ___  /_______ __  /_________  /_     ___________  /__(_)_  /_
           __  __ \  __ `/  __/  ___/_  __ \    _  _ \  __  /__  /_  __/
           _  /_/ / /_/ // /_ / /__ _  / / /    /  __/ /_/ / _  / / /_  
           /_.___/\__,_/ \__/ \___/ /_/ /_/     \___/\__,_/  /_/  \__/ 

	**** UC Libraries Record Loads Working Group ****

"""

def BrowseFiles():#open file explorer
	root=Tk()
	root.withdraw()
	filenameOUT = askopenfilename(filetypes=[("MARC files","*.mrc"),("XML files","*.xml"),("All the files","*.*")], title="R.L.W.G Batch Edit -- select input file")
	print type(filenameOUT)
	filename = filenameOUT
	
	root.destroy()
	print '\n\nSelected file: \"' + re.sub('.*/(.*?)$', '\\1\"', filename) 

	return filename

class utilityFunctions:

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
	
	def MarcEditXmlToMarc(self, x):
		mrcFileName = re.sub('.xml', '.mrc', x)
		print '\n<Converting from XML to MARC>\n'
		subprocess.call(['C:\\%s\\MarcEdit 6\\cmarcedit.exe' % MarcEditDir, '-s', x, '-d', mrcFileName, '-xmlmarc', '-marc8', '-mxslt', 'C:\\%s\\MarcEdit 6\\xslt\\MARC21XML2Mnemonic_plugin.xsl' % MarcEditDir])
		return mrcFileName

	def Standardize856_956(self, *args):
		output = []
		#Check 8/956 indicator 1 code for non http URL
		URLFieldInd1 = re.findall('=[8|9]56  [^4]..*', args[0])
		#if found, interrupt script with alert
		if URLFieldInd1:
			print '\a\a\nFound URL fields(s) with unexpected indicator:\n'
			for URLField in URLFieldInd1:
				print '\t' + URLField
			raw_input('\nPress <ENTER> to continue\n')
		#split file into list of lines
		x = args[0].split('\n')
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
				if len(args) > 1 and type(args[1]) == str:
						line = line + '$3{0} :'.format(args[1])
				#add standard $z
				line = line + '$zConnect to resource online'
				output.append(line)
			else:
				output.append(line)
		x = '\n'.join(output)
		return x

	def AddEresourceGMD(self, x):
		x = x.split('\n\n')
		GMD_out = []
		for record in x:
			if re.search('=245.*\$h', record) == None:
				if re.search('=245.*\$b', record):
					record = re.sub('(=245.*)(\s:\$b.*)', '\\1$h[electronic resource]\\2', record)
				elif re.search('=245.*\$c', record):
					record = re.sub('(=245.*)(/\$c.*)', '\\1$h[electronic resource] \\2', record)
				else:
					record = re.sub('(=245.*)', '\\1$h[electronic resource]', record)
			GMD_out.append(record)
		x = '\n\n'.join(GMD_out)
		return x

	def CharRefTrans(self, x):#Character reference translation table
		CharRefTransTable = {
			#Hex char refs
			'&#039;' : ['&#039;', '\"'],
			'&#146;' : ['&#146;', '\''],
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
			'&#247;' : ['&#247;', '/'],
			'&#xf7;' : ['&#xF7;', '/'],
			'&#249;' : ['&#249;', '{grave}u'],
			'&#250;' : ['&#250;', '{acute}u'],
			'&#251;' : ['&#251;', '{circ}u'],
			'&#252;' : ['&#252;', '{uml}u'],
			'&#253;' : ['&#253;', '{acute}y'],
			'&#254;' : ['&#254;', '{thorn}'],
			'&#255;' : ['&#255;', '{uml}y'],
			'&#268;' : ['&#268;', '{caron}C'],
			'&#269;' : ['&#269;', '{caron}c'],
			'&#x2BC;' : ['&#x2BC;', '\''],
			'&#345;' : ['&#345;', '{caron}r'],
			'&#34;' : ['&#34;', '\"'],
			'&#38;' : ['&#38;', '&'],
			'&#39;' : ['&#39;', '\''],
			'&#60;' : ['&#60;', '<'],
			'&#62;' : ['&#62;', '>'],
			'&#64257;' : ['&#64257;', 'fi'],
			'&#8194;' : ['&#8194;', ''],#em space
			'&#8195;' : ['&#8195;', '  '],
			'&#8203;' : ['&#8203;', ''],#zero width letter spacing
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
			'&#8234;' : ['&#8234;', ''],#unicode control character
			'&#8242;' : ['&#8242;', '\''],#prime
			'&#8482;' : ['&#8482;', '[TM]'],
			'&#8486;' : ['&#8486;', '[Ohm]'],
			'&#8722;' : ['&#8722;', '-'],
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
			'&#xAD;' : ['&#xAD;', '-'],
			'&#x0027;' : ['&#x0027;', '\''],
			'&#x0101;' : ['&#x0101;', '{macr}a', '{229}a'],
			'&#x142;' : ['&#x142;', '{lstrok}', '{177}'],
			'&#x153;' : ['&#x153;', '{oelig}', '{182}'],
			'&#x201A;' : ['&#x201A;', ','],
			'&#x2013;' : ['&#x2013;', '-'],
			'&#x2014;' : ['&#x2014;', '--'],
			'&#x2018;' : ['&#x2018;', '\''],
			'&#x2019;' : ['&#x2019;', '\''],
			'&#x2020;' : ['&#x2020;', ''],
			'&#x201E;' : ['&#x201E;', '\"', '\"'],
			'&#x2022;' : ['&#x2022;', '{middot}', '{168}'],
			'&#x2044;' : ['&#x2044;', '/', '{168}'],
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
		UnrecognizedCharRef = list(set(re.findall('&[\d|\w|#]*;', x)))
		if UnrecognizedCharRef:
			#sound bell
			print '\a\a\a\a\a\n<Found unrecognized characters>\n\n\t...generating error file\n'
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
		
	def DedupRecords(self, x):
		x = x.split('\n\n')
		x = filter(None, x)
		print '<Deduplicating records>\n\n\tInput Records: %s' % len(x)
		x = list(set(x))
		print '\n\tOutput Records: %s' % len(x)
		x.append('')
		x = "\n\n".join(x)
		return x

	def Bcode2CheckForManuscript(self, x):
		x = x.split('\n\n')
		out = []
		x = filter(None, x)
		for record in x:
			if record[12] == 't':
				if re.search('b2=[-ka4m3noefvhprsgcdjit][;|\n]', record):
					record = re.sub('b2=[-ka4m3noefvhprsgcdjit];', 'b2=a;', record)
				else:
					record = re.sub('(\$a\*bn=b[uint|olin].*)', '\\1b2=a;', record)
			out.append(record)
		x = '\n\n'.join(out)
		return x

	def Bcode2CheckForSerial(self, x):
		x = x.split('\n\n')
		out = []
		x = filter(None, x)
		for record in x:
			if record[13] == 's' or record[13] == 'b':
				if re.search('b2=[-ka4m3noefvhprsgcdjit][;|\n]', record):
					record = re.sub('b2=[-ka4m3noefvhprsgcdjit];', 'b2=s;', record)
				else:
					record = re.sub('(\$a\*bn=b[uint|olin].*)', '\\1b2=s;', record)
			out.append(record)
		x = '\n\n'.join(out)
		return x

class batchEdits:

	def ER_EAI_2nd(self, x, name='ER-EAI-2ND'):
		print '\nRunning change script '+ name + '\n'
		#print filename
		x = utilities.MarcEditBreakFile(filename)
		# Change =001 field to =002, and add 003
		x = re.sub('(?m)^=001  (.*)', '=002  \\1\n=003  ER-EAI-2nd', x)
		# ADD local 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\\\$a*b3=z;bn=buint;\n=949  \\1$luint$rs$t99\n=730  0\$aEarly American imprints (Online).$nSecond series,$pShaw-Shoemaker.$5OCU\n=506  \\$aAccess restricted to users at subscribing institutions\n=008', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_EAI_1st(self, x, name='ER-EAI-1st'):
		print '\nRunning change script '+ name + '\n'
		#print filename
		x = utilities.MarcEditBreakFile(filename)
		# Change =001 field to =002, and add 003
		x = re.sub('(?m)^=001  (.*)', '=002  \\1\n=003  ER-EAI-1st', x)
		# ADD local 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\\\$a*b3=z;bn=buint;\n=949  \\1$luint$rs$t99\n=730  0\$aEarly American imprints (Online).$nFirst series,$pEvans.$5OCU\n=506  \\\\$aAccess restricted to users at subscribing institutions\n=008', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x,'Readex')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OECD(self, x, name='ER-OECD'):
		print '\nRunning change script '+ name + '\n'
		#translate xml to MARC and break file
		x = utilities.MarcEditXmlToMarc(x)
		x = utilities.MarcEditBreakFile(x)
		def ER_OECD_iLibrary_Bks_NO300(x):
			# Change =001 field to =002, and add 003
			x = re.sub('(?m)^=001  (.*)', '=002  oecd_\\1\n=003  ER-OECD-iLibrary-Bks', x)
			# ADD local 730, 949 before supplied 008
			x = re.sub('(?m)^=008', r'=949  \\\$a*b3=z;bn=buint;\n=949  \\1$luint$rs$t99\n=730  0\$aOECD iLibrary.$pBooks.$5OCU\n=300  \\\\$a1 electronic text :$bdigital PDF file\n=506  \\\\$aAccess restricted to users at subscribing institutions\n=008', x)
			# 04-05-10 DELETE  lines
			x = re.sub('(?m)^=024.*\n', '', x)
			x = re.sub('(?m)^=035.*\n', '', x)
			return x

		def ER_OECD_iLibrary_Bks_300(x):
			# Change =001 field to =002, and add 003
			x = re.sub('(?m)^=001  (.*)', '=002  oecd_\\1\n=003  ER-OECD-iLibrary-Bks', x)
			# ADD local 730, 949 before supplied 008
			x = re.sub('(?m)^=008', r'=949  \\\$a*b3=z;bn=buint;\n=949  \\1$luint$rs$t99\n=730  0\$aOECD iLibrary.$pBooks.$5OCU\n=506  \\\\$aAccess restricted to users at subscribing institutions\n=008', x)
			#change 300 to standard form
			x = re.sub('(?m)^=300.*', r'=300  \\\\$a1 electronic text :$bdigital PDF file', x)
			# 04-05-10 DELETE  lines
			x = re.sub('(?m)^=024.*\n', '', x)
			x = re.sub('(?m)^=035.*\n', '', x)
			return x

		def ER_OECD_iLibrary_Serials(x):
			# Change =001 field to =002, and add 003
			x = re.sub('(?m)^=001  (.*)', '=002  oecd_\\1\n=003  ER-OECD-iLibrary-Serials', x)
			# ADD local 730, 949 before supplied 008
			x = re.sub('(?m)^=008', r'=949  \\\$a*b3=z;bn=buint;b2=s\n=949  \\1$luint$rs$t99\n=730  0\$aOECD iLibrary.$pSerials.$5OCU\n=506  \\\\$aAccess restricted to users at subscribing institutions\n=008', x)
			# 04-05-10 DELETE  lines
			x = re.sub('(?m)^=024.*\n', '', x)
			x = re.sub('(?m)^=035.*\n', '', x)
			return x


		x = x.split('\n\n')
		#create empty lists for sorting
		Serials = []
		Mono300 = []
		MonoSans300 = []
		#loop over list and sort into categories based on presence of fields
		for line in x:
			if re.search('=022', line) or re.search('=310', line) and re.search('=362', line):
				Serials.append(line)
			elif re.search('=300', line):
				Mono300.append(line)
			else:
				MonoSans300.append(line)
		#join and apply defined sub functions
		Serials = ER_OECD_iLibrary_Serials('\n\n'.join(Serials))
		Mono300 = ER_OECD_iLibrary_Bks_300('\n\n'.join(Mono300))
		MonoSans300 = ER_OECD_iLibrary_Bks_NO300('\n\n'.join(MonoSans300))
		#join all categories back into one string var
		x = Serials + '\n\n' + Mono300 + '\n\n' + MonoSans300
		#eliminate $a subfield and URL from 856
		x = re.sub('\$aoecd-ilibrary\.org', '', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'OECD iLibrary')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OCLC_WCS_SDebk(self, x, name='ER-OCLC-WCS-SDebk'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=003', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;\n=730  0\\$aScienceDirect eBook Series.$5OCU\n=003  ER-OCLC-WCS-SDebk\n=002  OCLC-WCS-SDebk\n=003', x)
		#change 856 to 956
		x = re.sub('(?m)^=856', '=956', x)
		#add colon to 956$3
		x = re.sub('(?m)\$3ScienceDirect', '$3ScienceDirect :', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_NBER(self, x, name='ER-NBER'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(filename)
		#change 001 to 002, retain first letter and insert initial code
		#x = re.sub('(?m)^=001  (.*)', '=002  nber \\1', x)
		x = re.sub('(?m)^=001  ', '=002  nber_', x) 
		#ADD 003, 006, 007, 533, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=830  \\0$aWorking paper series (National Bureau of Economic Research : Online)\n=730  0\\$aNBER working paper series online.$5OCU\n=533  \\\\$aElectronic reproduction.$bCambridge, Mass.$cNational Bureau of Economic Research,$d200-$e1 electronic text : PDF file.$fNBER working paper series.$nAccess restricted to patrons at subscribing institutions\n=007  cr\\mnu\n=006  m\\\\\\\\\\\\\\\\d\\\\\\\\\\\\\\\\\n=003  ER-NBER\n=008', x)
		# 530 field, change Hardcopy to Print
		x = re.sub('(?m)^(=530.*)Hardcopy(.*)', '\\1Print\\2', x)
		# 490 and 830 fields lack ISBD punctuation, supply where lacking
		x = re.sub('(?m)^(=490.*)[^ ;](\$v.*)', '\\1 ;\\2', x)
		x = re.sub('(?m)^(=830.*)[^ ;](\$v.*)', '\\1 ;\\2', x)
		# delete supplied 690 fields
		x = re.sub('(?m)^=690.*\n', '', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'NBER')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_Emrld_BME(self, x, name='ER-Emrld-BME'):
		print '\nRunning change script '+ name + '\n'
		#break the file: 
		x = utilities.MarcEditBreakFile(x)
		def Emrld_BME_changes(x):
			#insert 003, 730, 949 before supplied 003
			x = re.sub('(?m)^=003', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aEmerald business, management and economics ebook series.$5OCU\n=003  ER-Emrld-BME\n=003', x)
			#delete selected fields
			x = re.sub('(?m)^=072.*\n', '', x)
			x = re.sub('(?m)^=365.*\n', '', x)
			x = re.sub('(?m)^=366.*\n', '', x)
			#edit the 001 field
			x = re.sub('(?m)^=001  (.*)\n', '=002  emr-\\1\n', x)
			#edit the 650 subject fields
			x = re.sub(r'=650  \\7(.*)\$2.*', '=653  \\1', x)
			#change 856$z to standard form
			x = re.sub('(?m)^(=856.*)', '\\1$zConnect to resource online', x)
			return x
		#checks for presence of 856 field; if absent, sort out and add to error file
		
		Has856 = []
		No856 = []
		x = x.split('\n\n')
		for line in x:
			if re.search('=[89]56', line):
				Has856.append(line)
			else:
				No856.append(line)
		x = '\n\n'.join(Has856)
		#run batch edit on bibs with 856 present
		x = Emrld_BME_changes(x)
		#if any exist, save bibs with no 856 to file
		if len(No856) > 1:
			fileNo856 = open(filenameNoExt + 'no856_out.mrk', 'w')
			fileNo856.write('\n\n'.join(No856))
			fileNo856.close()
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'Emerald')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_CREDOREF(self, x, name='ER-CREDOREF'):
		print '\nRunning change script '+ name + '\n'
		#break the file
		x = utilities.MarcEditBreakFile(x)
		# Change 001 to 002, Insert 003, 730, 949 before supplied 245
		x = re.sub('(?m)^=001  ', '=002  credo_', x)
		# Insert 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aCredo reference.$5OCU\n=003  ER-CREDOREF\n=008', x)
		#translate char references, compile to MARC and save
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'Credo reference' )
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_CRCnetBASE(self, x, name='ER-CRCnetBASE'):
		x = utilities.MarcEditBreakFile(x)
		# Change =001 field to =002, and insert our local identifier value (003)
		x = re.sub('(?m)^=001  (.*)', '=002  crcnb \\1\n=003  ER-CRCnetBASE MRTS', x)
		# ADD 533, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\\\$a*b3=z;bn=buint;\n=949  \\1$luint$rs$t99\n=730  0\\$aCRCnetBASE.$5OCU\n=533  \\\\$aElectronic reproduction.$bBoca Raton, Fla. :$cCRC Press.$nMode of access: World Web Web.$nSystem requirements: Adobe Acrobat Reader.$nMade available through CRCnetBASE.$nAccess restricted to users at licensed institutions\n=008', x)
		# 04-05-10 DELETE  lines 015, 016, 945
		x = re.sub('=(016|015|945).*\n', '', x)
		#remove all occurances of 999 field
		x = re.sub('(?m)^=999.*\n', '', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'CRCnetBASE')
		x = utilities.CharRefTrans(x)
		x = utilities.DedupRecords(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def CasaliniInvoiceFix(self, x, name='Casalini Invoice Fix'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#move $f subfield in from $a subfield
		x = re.sub('(?m)^(=980.*)(\$a.*)(\$f\d*-\d*)(.*)', '\\1\\3\\2\\4', x)
		#add preceding ".o" to order number where absent
		x = re.sub('(?m)^(=935.*\$a)\.?(\d)', '\\1.o\\2', x)
		x = re.sub('(?m)^(=935.*\$a)(o\d)', '\\1.\\2', x)
		#eliminate 001 field
		x = re.sub('(?m)^=001.*\n', '', x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_SPRebk(self, x, name='ER-O/L-SPRebk'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aSpringerLink.$5OCU\n=730  0\\$aSpringer ebooks.$5OCU\n=003  ER-O/L-SPRebk\n=002  O/L-SPRebk\n=008', x)
		x = re.sub('(?m)\$3(SpringerLink|OhioLINK)\$', '$3\\1 :$', x)
		x = re.sub('(?m)\$zConnect to resource$', '$zConnect to resource online', x)
		x = re.sub('\$zConnect to resource \(off-campus access\)', '$zConnect to resource online (Off Campus Access)', x)
		x = utilities.DeleteLocGov(x)
		#x = utilities.Standardize856_956(x, 'SpringerLink')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_SPRebk_GAP2010ou(self, x, name='ER-O/L-SPRebk-GAP2010ou'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aSpringerLink.$5OCU\n=730  0\\$aSpringer ebooks.$5OCU\n=003  ER-O/L-SPRebk-GAP2010ou\n=002  O/L-SPRebk-GAP2010ou\n=008', x)
		x = re.sub('\$zConnect to electronic resource \(off-campus access\)', '$zConnect to resource online (Off Campus Access)', x)
		x = re.sub('\$zConnect to electronic resource', '$zConnect to resource online', x)
		x = re.sub('\$3SpringerLink', '$3SpringerLink :', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_SPRebk_GAP2011ou(self, x, name='ER-O/L-SPRebk-GAP2011ou'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aSpringerLink.$5OCU\n=730  0\\$aSpringer ebooks.$5OCU\n=003  ER-O/L-SPRebk-GAP2011ou\n=002  O/L-SPRebk-GAP2011ou\n=008', x)
		x = re.sub('\$zConnect to electronic resource \(off-campus access\)', '$zConnect to resource online (Off Campus Access)', x)
		x = re.sub('\$zConnect to electronic resource', '$zConnect to resource online', x)
		x = re.sub('\$3SpringerLink', '$3SpringerLink :', x)
		x = re.sub('\$3SpringerLINK', '$3SpringerLink :', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_SPRebk_OSU1(self, x, name='ER-O/L-SPRebk-OSU1'):
		print '\nRunning change script '+ name + '\n'
		sequential_num = raw_input('\n\nWhat is the number assigned to this file?')
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aSpringerLink.$5OCU\n=730  0\\$aSpringer ebooks.$5OCU\n=003  ER-O/L-SPRebk-OSU' + sequential_num + '\n=002  O/L-SPRebk-OSU\n=008', x)
		x = re.sub('(?m)\$zConnect to resource$', '$3SpringerLink :$zConnect to resource online', x)
		x = re.sub('\$zConnect to resource \(off-campus access\)', '$3SpringerLink :$zConnect to resource online (Off Campus Access)', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_SPRebk_OSU2(self, x, name='ER-O/L-SPRebk-OSU2'):
		print '\nRunning change script '+ name + '\n'
		sequential_num = raw_input('\n\nWhat is the number assigned to this file?')
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aSpringerLink.$5OCU\n=730  0\\$aSpringer ebooks.$5OCU\n=003  ER-O/L-SPRebk-OSU' + sequential_num + '\n=002  O/L-SPRebk-OSU\n=008', x)
		x = re.sub('(?m)\$3(SpringerLink|OhioLINK)\$', '$3\\1 :$', x)
		x = re.sub('(?m)\$zConnect to resource$', '$zConnect to resource online', x)
		x = re.sub('\$zConnect to resource \(off-campus access\)', '$zConnect to resource online (Off Campus Access)', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_OSO(self, x, name='ER-O/L-OSO'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aOxford scholarship online.$5OCU\n=003  ER-O/L-OSO\n=002  O/L-OSO\n=008', x)
		#edit proxy URLs
		x = re.sub('(?m)\$zConnect to electronic resource at Oxfordscholarship\.com$', '$3Oxford Scholarship Online :$zConnect to resource online', x)
		x = re.sub('(?m)\$zConnect to electronic resource at Oxfordscholarship\.com from Off Campus$', '$3Oxford Scholarship Online :$zConnect to resource online (Off Campus Access)', x)
		x = re.sub('(?m)^(=856.*rave.*?)(\$zConnect to resource online$)', '\\1$3OhioLINK :\\2', x)
		#x = re.sub('\(off-campus access\)', '(Off Campus Access)', x)
		x = utilities.DeleteLocGov(x)
		#x = utilities.Standardize856_956(x, 'Oxford Scholarship Online')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OCLC_WCS_Knovel(self, x, name='ER-OCLC-WCS-Knovel'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 003
		x = re.sub('(?m)^=003', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;\n=730  0\\$aKnovel library.$5OCU\n=003  ER-OCLC-WCS-Knovel\n=002  OCLC-WCS-Knovel\n=003', x)
		#Change hyperlink tag from 856 to 956
		x = re.sub('(?m)^=856(.*)', '=956\\1$3Knovel :', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'Knovel')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OCLC_WCS_ClinKey(self, x, name='ER-OCLC-WCS-ClinKey'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		# Delete 856 fields with ... 
		x = re.sub('(?m)^=856.*www.clinicalkey.com.au.*\n', '', x)
		x = re.sub('(?m)^=856.*www.lib.umn.edu/slog.phtm.*\n', '', x)
		#Insert 002, 003, 730, 949 before supplied 003
		x = re.sub('(?m)^=003', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;\n=730  0\\$aClinicalKey.$5OCU\n=003  ER-OCLC-WCS-ClinKey\n=002  OCLC-WCS-ClinKey\n=003', x)
		x = re.sub('\$3ClinicalKey', '', x)
		x = re.sub('\$3E-Book through ClinicalKey', '', x)
		#Change hyperlink tag from 856 to 956, add $3
		#x = re.sub('(?m)^=856(.*)', '=956\\1$3ClinicalKey :', x)
		# Change hyperlink tag from 856 to 956
		x = re.sub('(?m)^=856', '=956', x)
		#x = re.sub('(?m)^(=956.*)', '\\1$zConnect to resource online', x)
		x = utilities.AddEresourceGMD(x)
		x = utilities.Standardize856_956(x, 'ClinicalKey')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_OMC_Naxos(self, x, name='ER-O/L-OMC-Naxos'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aOhioLINK Music Center.$pNaxos music library.$5OCU\n=003  ER-O/L-OMC-Naxos\n=002  O/L-OMC-Naxos\n=008', x)
		#Change hyperlink tag from 856 to 956
		x = re.sub('(?m)^=856', '=956', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'OhioLINK OMC')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def MvIShipLists(self, x, name='MvI Shiplists'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
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
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def MvIFull(self, x, name='MvI Full'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		def MvIEresource(x):
			#add elements to 949 and append 049 control field
			x = re.sub('(=949.*)', '\\1$luint$t99$rs$z086\n=949  \\\\\$a*bn=buint', x)
			return x
		
		def MvIPrint(x):
			#add command fields to create print format item and set bib location to bula
			x = re.sub('(=949.*)', '\\1$lulagy$t01$rz$z086\n=949  \\\\\$a*bn=bula', x)
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
			#check for presence of GMD, sort based on such
			if re.search('\$h\[elect', record):
				MvIEresourceList.append(record)
			else:
				MvIPrintList.append(record)
	
		#join lists back into one string for each category and apply change script
		MvIEresourceList = MvIEresource('\n\n'.join(MvIEresourceList))
		MvIPrintList = MvIPrint('\n\n'.join(MvIPrintList))
		#join categories back into one file
		if len(MvIEresourceList) > 0 and len(MvIPrintList) > 0:
			MvIEresourceList = MvIEresourceList + '\n\n'
		x = MvIEresourceList + MvIPrintList
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_ORO(self, x, name='ER-O/L-ORO'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=003  ER-O/L-ORO\n=002  O/L-ORO\n=008', x)
		#Change supplied 730 lacking ending period, add .$5OCU to end of line
		x = re.sub('(?m)^(=730.*Oxford reference online\.)', '\\1$5OCU', x)
		x = re.sub('(?m)^(=730.*Oxford reference online(?!\.))', '\\1.$5OCU', x)
		x = utilities.Standardize856_956(x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_OR(self, x, name='ER-O/L-OR'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=003  ER-O/L-OR\n=002  O/L-OR\n=008', x)
		#Change supplied 730 lacking ending period, add .$5OCU to end of line
		x = re.sub('(?m)^(=730.*Oxford reference\.)', '\\1$5OCU', x)
		x = re.sub('(?m)^(=730.*Oxford reference(?!\.))', '\\1.$5OCU', x)
		x = utilities.Standardize856_956(x, 'Oxford Reference')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_Safari(self, x, name='ER-O/L-Safari'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 003
		x = re.sub('(?m)^=003', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aSafari books online.$5OCU\n=003  ER-O/L-Safari\n=002  O/L-Safari\n=003', x)
		#edit proxy URLs
		x = re.sub('\$zConnect to this resource online', '$3Safari (ProQuest) :$zConnect to resource online', x)
		x = re.sub('\(off-campus access\)', '(Off Campus Access)', x)
		x = re.sub('\$zConnect to electronic resource', '$3Safari(ProQuest) :$zConnect to resource online', x)
		x = re.sub('\(off-campus access\)', '(Off Campus Access)', x)
		#Change hyperlink tag from 856 to 956
		x = re.sub('(?m)^=856', '=956', x)
		#x = utilities.Standardize856_956(x, 'ProQuest')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_Sage_eRef(self, x, name='ER-O/L-Sage-eRef'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 003 
		x = re.sub('(?m)^=003', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aSage eReference.$5OCU\n=003  ER-O/L-Sage-eRef\n=002  O/L-Sage-eRef\n=003', x)
		x = utilities.Standardize856_956(x, 'SAGE Reference Online')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_GVRL(self, x, name='ER-O/L-GVRL'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=003', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aGale virtual reference library (Online).$5OCU\n=730  0\\$aGVRL.$5OCU\n=003  ER-O/L-GVRL\n=002  O/L-GVRL\n=003', x)
		x = utilities.Standardize856_956(x, 'OhioLINK EBC')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_ABC_Clio(self, x, name='ER-O/L-ABC-Clio'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 003
		x = re.sub('(?m)^=003', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aABC-Clio E-Books.$5OCU\n=003  ER-O/L-ABC-Clio\n=002  O/L-ABC-Clio\n=003', x)
		x = utilities.Standardize856_956(x, 'OhioLINK')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_ODRS(self, x, name='ER-O/L-ODRS'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		x = re.sub('(?m)^=003', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aOxford Digital Reference Shelf.$5OCU\n=002  O/L-ODRS\n=003  ER-O/L-ODRS\n=730  0\\$aODRS.$5OCU\n=003', x)
		x = utilities.Standardize856_956(x, 'OhioLINK EBC')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_InfoSci(self, x, name='ER-InfoSci'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#DELETE a number of fields, not all fields occur in every record
		x = re.sub('(?m)^(=001|=035|=040|=042|=050|=082|=590|=906|=925|=936|=952|=955|=963).*\n', '', x)
		#ADD 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aIGI Global Research Collection.$5OCU\n=730  0\\$aInfoSci.$5OCU\n=003  ER-InfoSci\n=002  InfoSci\n=008', x)
		#remove delim 3s
		x = re.sub('\$3Chapter PDFs via platform:', '', x)
		x = re.sub('\$3Article PDFs via platform:', '', x)
		#split records serial vs. monograph, add 949 b3=s to serials
		x = x.split('\n\n')
		serials = []
		monos = []
		for record in x:
			if re.search('=022', record):
				record = re.sub('=949.*\$a\*b3=z;bn=buint;', r'=949  \\\\$a*b3=z;bn=buint;b2=s;', record)
				serials.append(record)
			else:
				monos.append(record)
		if len(serials) > 0:
			x = '\n\n'.join(serials) + '\n\n' + '\n\n'.join(monos)
		else:
			x = '\n\n'.join(x)
			
		x = utilities.AddEresourceGMD(x)
		x = utilities.Standardize856_956(x, 'IGI InfoSci')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_YBP_DDA_disc(self, x, name='ER-YBP-DDAdisc'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#change 001 field tag to 002
		x = re.sub('(?m)^=001', r'=002', x)
		#add 003 and 949 command fields before supplied 002
		x = re.sub('(?m)^=002', r'=003  ER-YBP-DDA-disc\n=949  \\\\$a*b3=s;bn=buint;\n=949  \\1$luint$rs$t99\n=002', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_Sabin_Amer(self, x, name='ER-Sabin-Amer'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Change =001 to =002
		x = re.sub('(?m)^=001', r'=002', x)
		#Change value in =006 field
		x = re.sub('(?m)(^=006.*)j', '\\1d', x)
		#Insert 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;b3=z;\n=730  0\\$aSabin Americana, 1500-1926.$5OCU\n=003  ER-Sabin-Amer\n=008', x)
		#CHANGE indicators on URL
		x = re.sub('=856  ..', '=856  40', x)
		x = utilities.Standardize856_956(x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_NCCO(self, x, name='ER-NCCO'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Change =001 to =002
		x = re.sub('(?m)^=001', r'=002', x)
		#Change value in =006 field
		#x = re.sub('(?m)(^=006.*)j', '\\1d', x)
		#Insert 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;b3=z;\n=730  0\\$aNineteenth Century collections online.$5OCU\n=003  ER-NCCO\n=008', x)
		#CHANGE indicators on URL
		#x = re.sub('=856  ..', '=856  40', x)
		x = utilities.Standardize856_956(x)
		x = re.sub('(?m)\$3(Gale Cengage Learning, Nineteenth Century Collections Online)\$', '$3\\1 :$', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.Bcode2CheckForManuscript(x)
		x = utilities.Bcode2CheckForSerial(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_Ambrose_videos(self, x, name='ER-O/L-Ambrose-videos'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 003
		x = re.sub('(?m)^=003', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aAmbrose videos.$OCU\n=003  ER-O/L-Ambrose videos\n=002  O/L-Ambrose\n=003', x)
		x = utilities.Standardize856_956(x, 'OhioLINK DMC')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OCLC_WCS_IEEE_Xplore(self, x, name='ER-OCLC-WCS-IEEE-Xplore'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		# delete extraneous fields
		x = re.sub('(?m)^=938.*\n', '', x)
		# delete other 773 fields?
		x = re.sub('(?m)^=773  0\\\$tWiley InterScience.*\n', '', x)
		# Delete 856 fields with ... 
		x = re.sub('(?m)^=856.*www\.e-streams\.com.*\n', '', x)
		x = re.sub('(?m)^=856.*encompass\.library\.cornell.edu.*\n', '', x)
		x = re.sub('(?m)^=856.*site\.ebrary\.com.*\n', '', x)
		x = re.sub('(?m)^=856.*books\.google\.com.*\n', '', x)
		x = re.sub('(?m)^=856.*www3\.interscience\.wiley\.com.*\n', '', x)
		x = re.sub('(?m)^=856.*dx\.doi\.org.*\n', '', x)
		x = re.sub('(?m)^=856.*www\.myilibrary\.com.*\n', '', x)
		x = re.sub('(?m)^=856.*www\.netlibrary\.com.*\n', '', x)
		x = re.sub('(?m)^=856.*bvbr\.bib-bvb\.de.*\n', '', x)
		x = re.sub('(?m)^=856.*library\.stanford\.edu.*\n', '', x)
		x = re.sub('(?m)^=856.*public\.eblib\.com.*\n', '', x)
		x = re.sub('(?m)^=856.*www\.contentreserve\.com.*\n', '', x)
		#Insert 002, 003, 730, 949 before supplied 003
		x = re.sub('(?m)^=003', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;\n=730  0\\$aIEEE Xplore digital library.$5OCU\n=003  ER-OCLC-WCS-IEEE-Xplore\n=002  OCLC-WCS-IEEE-Xplore\n=003', x)
		# Change hyperlink tag from 856 to 956
		x = re.sub('(?m)^=856', '=956', x)
		x = utilities.Standardize856_956(x, 'IEEE Xplore')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_FFHS(self, x, name='ER-O/L-FFSH'):
		print '\nRunning change script '+ name + '\n'
		#break the MARC file
		x = utilities.MarcEditBreakFile(x)
		# Insert 002, 003, 730, 949 before supplied 003
		x = re.sub('(?m)^=003', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aFilms for the Humanities \& Sciences\n=003  ER-O/L-FFHS\n=002  O/L-FFHS\n=003', x)
		#change 856 to 956
		x = re.sub('(?m)^=856', '=956', x)
		#standard link field, delete TOCs, translate char references, make and save file
		x = utilities.Standardize856_956(x, 'OhioLINK DMC')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_WBNK(self, x, name='ER-WBNK'):
		#break the MARC file
		x = utilities.MarcEditBreakFile(x)
		#change 001 to 002
		x = re.sub('(?m)^=001  ', '=002  wbnk_', x)
		#ADD 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aWorld Bank eLibrary.$5OCU\n=003  ER-WBNK\n=008', x)
		#Delete space between indicators and subfield delimeter
		x = re.sub('=776  18 \$a', r'=776  18$a', x)
		# add access note to 533 field
		x = re.sub('(?m)(^=533.*)', '\\1$nAccess restricted to patrons at subscribing institutions.', x)
		#standardize link field, delete TOCs, translate char references, make and save file
		x = utilities.Standardize856_956(x, 'World Bank')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_ACLS(self, x, name='ER-O/L-ACLS'):
		#break the MARC file
		x = utilities.MarcEditBreakFile(x)
		# Insert 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=730  0\\$aHistory E-Book project.$5OCU\n=730  0\\$aACLS History E-Books.$5OCU\n=003  ER-O/L-ACLS\n=002  O/L-ACLS\n=008', x)
		#Delete TOC URLs
		x = utilities.DeleteLocGov(x)
		# Change hyperlink tag from 856 to 956
		x = re.sub('(?m)^=856', '=956', x)
		#standardize link field, delete TOCs, translate char references, make and save file
		x = utilities.Standardize856_956(x, 'ACLS Humanities E-Book')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_IET(self, x, name='ER-IET'):
		#breaktheMARCfile
		x = utilities.MarcEditBreakFile(x)
		#change001to002
		x = re.sub('(?m)^=001', '=002', x)
		#Insert 002,003,503,730,949 before supplied 008
		x = re.sub('(?m)=008',r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;b3=z;\n=003  ER-IET\n=730  0\\$aIET digital library.$pIET ebooks.$5OCU\n=506  \\\\$aAccess restricted to subscribing institutions\n=008', x)
		#removehyphensfrom020field
		x = x.split('\n')
		output = []
		for line in x:
			match = re.search('=020', line)
			if match:
				line = re.sub('-', '', line)
				output.append(line)
			else:
				output.append(line)
		x = '\n'.join(output)
		#addisbdpunctto245
		x = re.sub('(?m)(=245.*\w)(:\$b)', '\\1 \\2', x)
		x = re.sub('(?m)(=245.*\w)(\$b)', '\\1 :\\2', x)
		x = re.sub('(?m)(=245.*\w)(\$c)', '\\1 /\\2', x)
		#addisbdpucntto260
		x=re.sub('(?m)(=260.*\w)(\$b)', '\\1 :\\2', x)
		x=re.sub('(?m)(=260.*\w)(\$c)', '\\1, \\2', x)
		#add|h[electronicresource]totitlestring
		x=utilities.AddEresourceGMD(x)
		#change300fieldtostandard
		x=re.sub('(?m)=300.*',r'=300\\\\$a1electronictext:$bdigitalPDFfile',x)
		#strip6507
		x=re.sub('(?m)=650\\\\7.*\n', '', x)
		#normalizeseriesheadings
		x = re.sub('(?m)(=830  \\\\0\$a)Telecommunications', '\\1IET telecommunications series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Control Engineering', '\\1IET control engineering series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Professional Applications of Computing', '\\1Professional applications of computing series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)History of Technology', '\\1IET history of technology series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Radar, Sonar, Navigation and Avionics', '\\1IET radar, sonar, navigation and avionics series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Circuits,Devices and Systems','\\1IET circuits, devices and systems series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Electrical Technology','\\1IET electrical measurement series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Power and Energy','\\1IETpower and energy series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Electromagnetic Waves','\\1IET electromagnetic wave sseries',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Manufacturing','\\1IEEmanufacturingseries',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Management of Technology','\\1IET management of technology series',x)
		x = re.sub('(?m)(=830  \\\\0\$a)Renewable Energy','\\1IET renewable energy series',x)
		#shorten=008'dateentered'elementtoconformwithmarkstandard--yearshouldonlybedecade
		x = re.sub('(?m)(=008  )20', '\\1', x)
		#standardizelinkfield,deleteTOCs,translatecharreferences,makeandsavefile
		utilities.Standardize856_956(x, 'IET ebooks')
		utilities.CharRefTrans(x)
		utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_UAdelaide(self, x, name='ER-UAdelaide'):
		#breaktheMARCfile
		x = utilities.MarcEditBreakFileTranslateToMarc8(x)
		#change001to002
		x = re.sub('(?m)^=001  ', '=002  uAdelaide_', x)
		#Insert 003,730,949 before supplied 008
		x = re.sub('(?m)^=008',r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;b3=z;\n=003  ER-UAdelaide\n=730  0\\$aUniversity of Adelaide Library eBooks.$5OCU\n=008', x)
		#standardizelinkfield,deleteTOCs,translatecharreferences,makeandsavefile
		x = utilities.Standardize856_956(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_ASP_CTV(self, x, name='ER-ASP-CTV'):
		#breaktheMARCfile
		x = utilities.MarcEditBreakFileTranslateToMarc8(x)
		#change001to002
		x = re.sub('(?m)^=001', '=002', x)
		#Insert 003,730,949 before supplied 008
		x = re.sub('(?m)^=008',r'=949  \\1$luint$rs$t99\n=949  \\\\$a*bn=buint;b3=z;\n=003  ER-ASP-CTV\n=710  2\\$aAlexander Street Press\n=730  0\\$aAlexander Street Counseling.$5OCU\n=730  0\\$aCounseling and therapy in video.$5OCU\n=008', x)
		#standardizelinkfield,deleteTOCs,translatecharreferences,makeandsavefile
		x = utilities.Standardize856_956(x, 'Alexander Street Press')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_Wiley(self, x, name='ER-O/L-Wiley-InterSci'):
		print '\nRunning change script '+ name + '\n'
		#breaktheMARCfile
		x = utilities.MarcEditBreakFile(x)
		#Insert 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=003  ER-O/L-Wiley-InterSci\n=002  O/L-Wiley-InterSci\n=730  0\\$aWiley online library.$5OCU\n=730  0\\$aWiley InterScience ebooks.$5OCU\n=008', x)
		#edit proxy URLs
		x = re.sub('(?m)^=856  40\$3Wiley Online Library', '=856  40$3Wiley Online Library :', x)
		x = re.sub('(?m)\$zConnect to resource$', '$zConnect to resource online', x)
		x = re.sub('\$zConnect to resource \(off-campus\)', '$zConnect to resource online (Off Campus Access)', x)
		#standardizelinkfield,deleteTOCs,translatecharreferences,makeandsavefile
		#x = utilities.Standardize856_956(x, 'Wiley Online')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.AddEresourceGMD(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_APA_PBK(self, x, name='ER-APA-PBK'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(filename)
		#change 001 to 002, retain first letter and insert initial code
		x = re.sub('(?m)^=001  ', '=002  Psycbook_', x)
		#ADD 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aPsycBOOKS.$5OCU\n=730  0\\$aAPA PsycBOOKS.$5OCU\n=003  ER-APA-PBK\n=008', x)
		#remove Table of contents URLs
		x = re.sub('(?m)^=856.*Table of contents.*\n', '', x)
		#remove $3Full text available
		x = re.sub('\$3Full text available', '', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x, 'EBSCO')
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_LN_SSDC_2(self, x, name='ER-LN-SSCD-2'):
		def ER_LN_SSDC_2_NO086(x):
			xProcessed = []
			for record in x:
				record = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=008', record)
				xProcessed.append(record)
			return xProcessed

		def ER_LN_SSDC_2_HAS086(x):
			xProcessed = []
			for record in x:
				record = re.sub('(?m)^=008', r'=949  \\1$luint$t99$rs$z086$a\n=008', record)
				match086list = re.findall('(?<==086  \d\\\\\$a).*', record)
				record = re.sub('(\$rs\$z086\$a)', '\\1' + match086list[0], record)
				if len(match086list) > 1:
					for match in match086list[1:]:
						record = re.sub('(\n=008)', r'$a' + match + '\\1', record)
				xProcessed.append(record)
			return xProcessed

		#break the MARC file
		x = utilities.MarcEditBreakFile(x)
		#edit Character Ref "&amp;amp;"
		x = re.sub('&amp;amp;', '&', x)
		#change 001 to 002
		x = re.sub('(?m)^=001', '=002', x)
		#ADD 002, 003, 730, before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aProQuest U.S. serial set digital collection.$5OCU\n=003  ER-LN-SSDC-2\n=002  LN-SSDC-2\n=008', x)
		x = x.split('\n\n')
		#create empty lists for sorting
		Has086 = []
		No086 = []
		#loop over list and sort into categories based on presence of fields
		for record in x:
			if re.search('=086', record):
				Has086.append(record)
			else:
				No086.append(record)

		if Has086 > 0:
			Has086processed = ER_LN_SSDC_2_HAS086(Has086)
		if No086 > 0:
			No086processed = ER_LN_SSDC_2_NO086(No086)
		joinedprocessed = Has086processed + No086processed
		x = '\n\n'.join(joinedprocessed)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_PQ_SSDC(self, x, name='ER-PQ-SSDC'):
		def ER_PQ_SSDC_NO086(x):
			xProcessed = []
			for record in x:
				record = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=008', record)
				xProcessed.append(record)
			return xProcessed

		def ER_PQ_SSDC_HAS086(x):
			xProcessed = []
			for record in x:
				record = re.sub('(?m)^=008', r'=949  \\1$luint$t99$rs$z086$a\n=008', record)
				match086list = re.findall('(?<==086  \d\\\\\$a).*', record)
				record = re.sub('(\$rs\$z086\$a)', '\\1' + match086list[0], record)
				if len(match086list) > 1:
					for match in match086list[1:]:
						record = re.sub('(\n=008)', r'$a' + match + '\\1', record)
				xProcessed.append(record)
			return xProcessed

		#break the MARC file
		x = utilities.MarcEditBreakFile(x)
		#edit Character Ref "&amp;amp;"
		x = re.sub('&amp;amp;', '&', x)
		#change 001 to 002
		x = re.sub('(?m)^=001', '=002', x)
		#ADD 002, 003, 730, before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aProQuest U.S. serial set digital collection.$5OCU\n=003  ER-PQ-SSDC\n=002  PQ-SSDC\n=008', x)
		x = x.split('\n\n')
		#create empty lists for sorting
		Has086 = []
		No086 = []
		#loop over list and sort into categories based on presence of fields
		for record in x:
			if re.search('=086', record):
				Has086.append(record)
			else:
				No086.append(record)

		if Has086 > 0:
			Has086processed = ER_PQ_SSDC_HAS086(Has086)
		if No086 > 0:
			No086processed = ER_PQ_SSDC_NO086(No086)
		joinedprocessed = Has086processed + No086processed
		x = '\n\n'.join(joinedprocessed)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_PQ_CHDC(self, x, name='ER-PQ-CHDC'):
		def ER_PQ_CHDC_NO086(x):
			xProcessed = []
			for record in x:
				record = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=008', record)
				xProcessed.append(record)
			return xProcessed

		def ER_PQ_CHDC_HAS086(x):
			xProcessed = []
			for record in x:
				record = re.sub('(?m)^=008', r'=949  \\1$luint$t99$rs$z086$a\n=008', record)
				match086list = re.findall('(?<==086  \d\\\\\$a).*', record)
				record = re.sub('(\$rs\$z086\$a)', '\\1' + match086list[0], record)
				if len(match086list) > 1:
					for match in match086list[1:]:
						record = re.sub('(\n=008)', r'$a' + match + '\\1', record)
				xProcessed.append(record)
			return xProcessed

		#break the MARC file
		x = utilities.MarcEditBreakFile(x)
		#edit Character Ref "&amp;amp;"
		x = re.sub('&amp;amp;', '&', x)
		#change 001 to 002
		x = re.sub('(?m)^=001', '=002', x)
		#ADD 002, 003, 730, before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aProQuest Congressional Hearings digital collection.$5OCU\n=003  ER-PQ-CHDC\n=002  PQ-CHDC\n=008', x)
		x = x.split('\n\n')
		#create empty lists for sorting
		Has086 = []
		No086 = []
		#loop over list and sort into categories based on presence of fields
		for record in x:
			if re.search('=086', record):
				Has086.append(record)
			else:
				No086.append(record)

		if Has086 > 0:
			Has086processed = ER_PQ_CHDC_HAS086(Has086)
		if No086 > 0:
			No086processed = ER_PQ_CHDC_NO086(No086)
		joinedprocessed = Has086processed + No086processed
		x = '\n\n'.join(joinedprocessed)
		x = utilities.DeleteLocGov(x)
		x = utilities.Standardize856_956(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_SPIEeBook(self, x, name='ER-SPIE-eBook'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#DELETE a number of fields, not all fields occur in every record
		x = re.sub('(?m)^(=001|=035|=040|=042|=050|=082|=590|=906|=925|=936|=952|=955|=963).*\n', '', x)
		#ADD 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aSPIE eBooks.$5OCU\n=730  0\\$aSPIE digital library.$pSPIE eBooks.$5OCU\n=003  ER-SPIE-eBook\n=002  SPIE-eBook\n=008', x)
		x = utilities.Standardize856_956(x, 'SPIE digital library')
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_MOMW_2(self, x, name='ER-MOMW-2'):
		print '\nRunning change script '+ name + '\n'
		x = utilities.MarcEditBreakFile(x)
		#DELETE a number of fields, not all fields occur in every record
		x = re.sub('(?m)^(=035|=040|=042|=050|=082|=590|=906|=925|=936|=952|=955|=963).*\n', '', x)
		#CHANGE 001 to 002
		x = re.sub('(?m)^=001', '=002', x)
		#ADD 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aMaking of the modern world (Online).$5OCU\n=003  ER-MOMW-2\n=002  MOMW-2\n=008', x)
		#ADD subfield delimiter to series
		x = re.sub('(=[490|830].*?) (Part.*)', '\\1$n\\2', x) 
		#CHANGE indicators on URL
		x = re.sub('=856  ..', '=856  40', x)
		x = utilities.Standardize856_956(x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_DOAB(self, x, name='ER-DOAB'):
		print '\nRunning change script '+ name + '\n'
		langdict = MARC_lang.LangToMarcCode
		x = utilities.MarcEditBreakFile(x)
		#CHANGE 001 to 002
		x = re.sub('(?m)^=001  ', '=002  doab_', x)
		#ADD 002, 003, 730, 949 before supplied 008
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aDirectory of open access books.$5OCU\n=003  ER-DOAB\n=008', x)
		#Standardize 007
		x = re.sub('(?m)^=007.*', '=007  cr|mnu', x)
		#Remove empty page numbers 300
		x = re.sub('(1 electronic resource)( \( p.\))', '\\1', x)
		#CHANGE indicators on URL
		x = re.sub('=856  ..', '=856  40', x)
		#ADD $3 to =856 field
		x = re.sub('(=856.*)', '\\1$3Download PDF :', x)
		#Fix spaces surrounding comma
		x = re.sub(' ,', ',', x)
		x = re.sub(',(\w)', ', \\1', x)
		#add ISBD punct to =260 field
		x = re.sub('(=260.*)(\$c)', '\\1,\\2', x)
		#add ISBD punct to =245
		x = re.sub('(?m)(=245.*?)(:)', '\\1 \\2$b', x)
		x = re.sub('(?m)(=245.*\w)(\$c)', '\\1 /\\2', x)
		x = re.sub('(?m)(=245.*\$b)( )', '\\1', x)
		#remove html markup
		x = re.sub('(?i)<br/>', '', x)
		x = re.sub('(?i)<br>', '', x)
		x = re.sub('(?i)<p/>', '', x)
		x = re.sub('(?i)<p>', '', x)
		x = re.sub('(?i)<i>', '', x)
		#ADD eresource GMD
		x = utilities.AddEresourceGMD(x)
		#add =008 language code
		x = x.split('\n\n')
		#create empty list
		xout = []
		for record in x:
			#get date from =260$c
			date260 = re.search('(?<=\$c)\d\d\d\d', record)
			if date260:
				date260 = date260.group()
			else:#set date to unknown 200-
				date260 = '200u'
				record = re.sub('(=260.*?)\$c', '\\1$c200?', record)
			#get lang from =546
			lang546 = re.search('(?<==546.{6})(.*)', record)
			if lang546:
				lang546 = lang546.group()
				if ';' in lang546:
					lang546 = re.sub(';.*', '', lang546)
				if lang546 in langdict:
					lang008 = langdict[lang546]
				else:
					lang008 = 'eng'
			else:#set lang to english where no =546
				lang008 = 'eng'
			#set =245 skip/indicator 2
			Skip245 = re.search('(?<==245  1\\\\\$a).{4}', record)
			if Skip245:
				if re.match('The\s', Skip245.group()):
					f245ind2 = '4'
				elif re.match('An\s', Skip245.group()):
					f245ind2 = '3'
				elif re.match('A\s', Skip245.group()):
					f245ind2 = '2'
				else:
					f245ind2 = '0'
				record = re.sub('=245  1.(\$a)', '=245  1%s\\1' % f245ind2, record)
			record = re.sub('=008.*', r'=008  120521s%s\\\\\\\\xx\\\\\\\\\\\\o\\\\\\\\\\0\\\\\\u\\%s\\|' % (date260, lang008), record)
			xout.append(record)
		x = '\n\n'.join(xout)
		x = utilities.Standardize856_956(x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_YBPeappr(self, x, name='ER-O/L-YBPeappr '):
		print '\nRunning change script '+ name + '\n'
		#break the file
		x = utilities.MarcEditBreakFile(x)
		#insert 949, 002, 003 before 008 field
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=003  ER-O/L-YBPeappr\n=002  O/L-YBPebkpilot\n=008', x)
		#change $z message to standard
		x = re.sub('(?m)\$zConnect to resource$', r'$zConnect to resource online', x)
		x = re.sub('\$zConnect to resource \(Off-campus access\)', '$zConnect to resource online (Off Campus Access)', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.AddEresourceGMD(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_YBPeDDA_disc(self, x, name='ER-O/L-YBPeDDA-disc'):
		print '\nRunning change script '+ name + '\n'
		#break the file
		x = utilities.MarcEditBreakFile(x)
		#insert 949, 002, 003 before 008 field
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=948  \\\\$aARL STATS - OLYPBedda record; record stat when replaced with OCLC record; tjac\n=003  {}\n=008'.format(name), x)
		
		#split to get docID and insert in =002
		x = x.split('\n\n')
		x = filter(None, x)
		try:
			x = [record + '\n=002  ebr{}'.format(re.search('(?m)docID=(\d*)', record).group(1)) for record in x]
		except AttributeError:
			raw_input('\a\a\a\n\tRECORD MISSING EBRARY docID!!!!!!!!!!')
			sys.exit()
		#print x
		x = '\n\n'.join(x)
		#change $z message to standard
		x = re.sub('(?m)\$zConnect to resource$', r'$zConnect to resource online', x)
		x = re.sub('\$zConnect to resource \(Off-campus access\)', '$zConnect to resource online (Off Campus Access)', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.AddEresourceGMD(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_OL_YBPeDDA_inv(self, x, name='ER-O/L-YBPeDDA-inv'):
		print '\nRunning change script '+ name + '\n'
		#break the file
		x = utilities.MarcEditBreakFile(x)
		#insert 949, 002, 003 before 008 field
		x = re.sub('(?m)^=008', r'=949  \\1$lolink$rs$t99\n=949  \\\\$a*bn=bolin;\n=948  \\\\$aARL STATS - OLYPBedda record; record stat when replaced with OCLC record; tjac\n=003  {}\n=008'.format(name), x)
		
		#split to get docID and insert in =002
		x = x.split('\n\n')
		x = filter(None, x)
		try:
			x = [record + '\n=002  ebr{}'.format(re.search('(?m)docID=(\d*)', record).group(1)) for record in x]
		except AttributeError:
			raw_input('\a\a\a\n\tRECORD MISSING EBRARY docID!!!!!!!!!!')
			sys.exit()
		#print x
		x = '\n\n'.join(x)

		#change $z message to standard
		x = re.sub('(?m)\$zConnect to resource$', r'$zConnect to resource online', x)
		x = re.sub('\$zConnect to resource \(Off-campus access\)', '$zConnect to resource online (Off Campus Access)', x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.AddEresourceGMD(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

	def ER_Momentum(self, x, name='ER-Momentum'):
	#used OCLC bibs instead of supplied bibs; added 003 and 730 as below
		print '\nRunning change script '+ name + '\n'
		#break the file
		x = utilities.MarcEditBreakFile(x)
		#insert 949, 002, 003, 730 before 008 field
		#x = re.sub('(?m)^=001', '=002', x)
		#x = re.sub('(?m)^=008', '=003  ER-Momentum\n=008', x)
		x = re.sub('(?m)^=008', r'=949  \\1$luint$rs$t99\n=949  \\\\$a*b3=z;bn=buint;\n=730  0\\$aMomentum Press ebooks.$5OCU\n=003  ER-Momentum\n=008', x)
		x = utilities.Standardize856_956(x)
		x = utilities.DeleteLocGov(x)
		x = utilities.CharRefTrans(x)
		x = utilities.MarcEditSaveToMRK(x)
		x = utilities.MarcEditMakeFile(x)
		return x

reStart = ''

while reStart == '' or reStart == 'y':
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
	filename = BrowseFiles()

	#get filename and strip extension
	filenameNoExt = re.sub('.\w*$', '', filename)

	#create dictionary/menu of all available change scripts
	ChangeScriptsDict = utilities.listChangeScripts(BatchEdits)

	#select change script by index in dictionary
	SelectedProcess = utilities.ScriptSelect()
	methodToCall = getattr(BatchEdits, ChangeScriptsDict[int(SelectedProcess)][0])
	result = methodToCall(filename)
	print '\nOutput File...\n\n\t\tEditing finished '
	reStart = ''
	while reStart != 'y' and reStart != 'n':
		reStart = raw_input('\n\n\nWould you like to run BatchCave again? (y/n)\n\n\n')

