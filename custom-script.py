import sublime
import sublime_plugin

#=============================
#====    DEVELOPER DETAILS  ==
#=============================

# DEV: NIRAJ CHOUDHARY
# GIT_URL: https://github.com/nkchoudhary2000


#==============================
#=====     NUMBER FILL       ==
#==============================
class ListGenerator(sublime_plugin.TextCommand):
	def run(self, edit):
		first_line = self.view.substr(self.view.sel()[0]).split('\"')
		chk_alpha = False
		if first_line[0].isdigit():
			counter = int(first_line[0]) - 1
		elif first_line[0].isalpha():
			counter = ord(first_line[0])
			chk_alpha = True
		else:
			counter = 0

		for sel in self.view.sel():
			counter += 1
			if chk_alpha:
				strCounter = str(chr(counter - 1))
				if strCounter == "Z":
					counter = 65
				elif strCounter == "z":
					counter = 97
			else:
				strCounter = str(counter)

	
			each_line = self.view.substr(sel).split("\"")
			print (each_line)			
			if len(each_line) >= 2:
				strCounter += "\"" + each_line[1]

			self.view.replace(edit, sel, strCounter)

#==============================
#=====      UPPER CASE       ==
#==============================

class UpperCaseGenerator(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in self.view.sel():
			input = self.view.substr(sel)
			input = input.upper()
			self.view.replace(edit,sel,input)


#==============================
#=====      LOWER CASE       ==
#==============================

class LowerCaseGenerator(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in self.view.sel():
			input = self.view.substr(sel)
			input = input.lower()
			self.view.replace(edit,sel,input)




		