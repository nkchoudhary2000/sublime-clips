import sublime_plugin, re, sublime
import sys
import os



def fixUniCode(input):
    input = input.replace(u"\u2019", "'").replace(u"\u2018", "'").replace(u"\u201C", "\"").replace(u"\u201D", "\"").replace(u"\u2014", '&amp;mdash;').replace(u"\u2013", '&amp;ndash;')
    input = re.sub('&\s', '&amp; ',input)
    return input


def make_labels(input, itemOP, splitter):
    surveyItems = []
    i = 1
    input = re.sub(r"\n([\s]*)\n", r"\n", input)
    input = re.sub(r"[_]{2,}", r"", input)
    # input = re.sub(r"[\n]{2,}", r"\n", input)
    input = input.split(splitter)
    for x in input:
        #Trying to  have the ability to do all different cases
        #Looking for most complicated first
        #Label = r or c or ch + any combo 4 characters long
        rowAB = re.search(r"^(?:r|ch|c)([a-zA-Z0-9]{1,4})(?:[.:\)]*?)(?:[\s\t]+?)(.+)$", x.strip())
        #Number at the beginning 4 digits long
        rowDD = re.search(r"^([0-9]{1,4})(?:[.:\)]?)(?:[\s\t]+)(.+)$", x.strip())
        #Numbers or letters 2 characters long. Must have ".:\)"
        rowAA = re.search(r"^([a-zA-Z0-9]{1,2})(?:[.:)])(?:[\s\t]+?)(.+)$", x.strip())
        #For rating question columns
        rowCC = re.search(r"^([0-9]{1,2})$", x.strip())
        #No label found. Just start labeling at 1 and increment
        rowZZ = re.search(r"^(.*)$", x.strip())

        if itemOP =="c":

            if rowAB:
                rowLabel = itemOP + rowAB.group(1)
                rowText = rowAB.group(2) + "<br/>" + rowAB.group(1)
                rowNum = rowAB.group(1)
                i += 1
                print ("option 3")

            elif rowAA:
                rowLabel = itemOP + rowAA.group(1)
                rowText = rowAA.group(2) + "<br/>" + rowAA.group(1)
                rowNum = rowAA.group(1)
                i += 1
                print ("option 1")

            elif rowCC:
                rowLabel = itemOP + rowCC.group(1)
                rowText = rowCC.group(1)
                rowNum = rowCC.group(1)
                i += 1
                print ("option 1")

            elif rowDD:
                rowLabel = itemOP + rowDD.group(1)
                rowText = rowDD.group(2) + "<br/>" + rowDD.group(1)
                rowNum = rowDD.group(1)
                i += 1
                print ("option 2")

            else:
                rowText = rowZZ.group(1)
                colFix = re.search(r"([a-zA-Z0-9]+)(?:[.]{1})", rowText)
                rowNum = rowZZ.group(1)

                if colFix:
                    rowText = colFix.group(1).split('c')[1]

                rowLabel = itemOP + str(i)
                i += 1
                print ("option 4")

            print ([rowLabel, rowText, rowNum])

        else:
            if rowAA:
                rowLabel = itemOP + rowAA.group(1)
                rowText = rowAA.group(2)
                rowNum = rowAA.group(1)

            elif rowDD:
                rowLabel = itemOP + rowDD.group(1)
                rowText = rowDD.group(2)
                rowNum = rowDD.group(1)

            elif rowAB:
                rowLabel = itemOP + rowAB.group(1)
                rowText = rowAB.group(2)
                rowNum = rowAB.group(1)

            else:
                rowLabel = itemOP + str(i)
                rowText = rowZZ.group(1)
                rowNum = rowZZ.group(1)
                i += 1

        rowText = re.sub("&\s", "&amp;", rowText)
        rowText = re.sub(r"((?i)other|specify)([:)]*)([\s]*)([_]+)", r"\1\2", rowText)

        spec = re.search(r"((?i)other.*specify)", rowText)
        extra = ""

        if spec:
            extra=" open=\"1\" openSize=\"10\" randomize=\"0\""

        surveyItems.append([rowLabel, rowText, extra, rowNum])
    return surveyItems

class MakeHtmlCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()
            input = ''

            for sel in sels:
                input = self.view.substr(sel).strip()
                input = input.split('\n')
                printPage = ''
                inputPage = ''
                for x in input:
                    if x == "":
                        inputPage += "<br/><br/>\n"
                    else:
                        inputPage += x + "\n"
                printPage = """<html label=\"\" where=\"survey\">
%s
</html>""" % inputPage

            self.view.replace(edit, sel, printPage)
        except Exception as e:
            print (e)

#Could totally use sub for this. Wasn't thinking
class MatchRowValuesCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()
            input = ''

            for sel in sels:
                input = self.view.substr(sel).strip()
                input = input.split('\n')
                printPage = ''
                i = 1

                for x in input:
                    findL = re.search(r'(<row|<choice|<col)(.*)(label="(r|c|ch)(\d*)")(.*)$', x.strip())
                    if findL:
                        valueAdded = "  " + findL.group(1) + findL.group(2) + findL.group(3) + ' value=\"' +findL.group(5) + '\"' + findL.group(6)
                    else:
                        findL = re.search(r'(<row|<choice|<col)(.*)(label="(r|c|ch)(.*)")(.*)$', x.strip())
                        valueAdded = "  " + findL.group(1) + findL.group(2) + findL.group(3) + ' value=\"' + str(i) + '\"' + findL.group(6)
                        i += 1
                    printPage += valueAdded + "\n"

                self.view.replace(edit, sel, printPage)
        except Exception as e:
            print (e)

class StripCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            sels = self.view.sel()
            input = ""
            printPage = ""

            for sel in sels:
                input = self.view.substr(sel).strip()
                input = input.split('\n')

                for x in input:
                    findCon = re.search(r'>(.*)<', x.strip())
                    printPage += findCon.group(1) + "\n"

                self.view.replace(edit, sel, printPage)
        except Exception as e:
            print (e)

class ImageTagsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            for sel in self.view.sel():
                nLs = self.view.split_by_newlines(sel)
                rowVs = []
                printPage = ""

                for x in nLs:
                    rowVs.append(self.view.substr(x).strip())

                for x in rowVs:
                    if x != "":
                        printPage += "  <img src=\"[rel " + x + "]\" alt=\"Image\" class=\"custImage\" />" + '\n'

                self.view.replace(edit, sel, printPage)
        except Exception as e:
            print (e)

class ReverseOrderCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        try:

            for sel in self.view.sel():
                nLs = self.view.split_by_newlines(sel)
                rowVs = [self.view.substr(x).strip() for x in nLs]
                printPage = ""

                for x in reversed(rowVs):
                    printPage += x + '\n'

                self.view.replace(edit, sel, printPage)
        except Exception as e:
            print (e)


def question_merge(splNums, qLabel):
    Qs = qLabel + "_1"
    for x in range(2, int(splNums)+1):
        Qs += ", " + qLabel + "_" + str(x)
    mergeExec = """
<exec>
splitQuestions = ["""+Qs+"""]

for question in splitQuestions:
    for r in question.rows:
        if r.val is not None:
            """+qLabel+""".attr(r.label).val = r.val
            if hasattr(r, 'open'):
                """+qLabel+""".attr(r.label).open = r.open
</exec>
"""
    return mergeExec

def make_split_questions(self, qType, splNums, rowNums, qLabel, qComment, qItems, qTitle):
    mkSplits = ""
    jumpBy = int(rowNums / splNums)
    firstNum = 0
    secNum = jumpBy


    for x in range(1, splNums+1):
        if x == 1:
            mkSplits += """
<"""+qType+""" label=\""""+qLabel+"""_1\" shuffle=\"rows\" where=\"survey,notdp\" rowCond=\"row.label in [r.label for r in """+qLabel+"""_1.rows.order[0:"""+str(secNum)+"""]]\">
"""+qTitle+qComment+qItems+"""
</"""+qType+""">
<suspend/>
"""
            firstNum += jumpBy
            secNum += jumpBy

        elif x == splNums:
            mkSplits += """
<"""+qType+""" label=\""""+qLabel+"""_"""+str(x)+"""\" onLoad=\"copy('"""+qLabel+"""_1', rows=True"""+self.qCol+self.qChoice+""")\" shuffle=\"rows\" where=\"survey,notdp\" rowCond=\"row.label in [r.label for r in """+qLabel+"""_1.rows.order["""+str(firstNum)+""":]]\">
"""+qTitle+qComment+"""
<exec>
"""+qLabel+"""_"""+str(x)+""".rows.order = """+qLabel+"""_1.rows.order
</exec>
</"""+qType+""">
<suspend/>
"""
        else:
            mkSplits += """
<"""+qType+""" label=\""""+qLabel+"""_"""+str(x)+"""\" onLoad=\"copy('"""+qLabel+"""_1', rows=True"""+self.qCol+self.qChoice+""")\" shuffle=\"rows\" where=\"survey,notdp\" rowCond=\"row.label in [r.label for r in """+qLabel+"""_1.rows.order["""+str(firstNum)+""":"""+str(secNum)+"""]]\">
"""+qTitle+qComment+"""
<exec>
"""+qLabel+"""_"""+str(x)+""".rows.order = """+qLabel+"""_1.rows.order
</exec>
</"""+qType+""">
<suspend/>
"""
            firstNum += jumpBy
            secNum += jumpBy


    return mkSplits

def make_original_question(self, qType, qLabel, qComment, qItems, qTitle):
    question = """
<"""+qType+""" label=\""""+qLabel+"""\" where=\"execute\">
"""+qTitle+qComment+"""
"""+qItems+"""
</"""+qType+""">
<suspend/>"""
    return question


class SplitQuestionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        splNums = 0
        # qHead = ''
        qType = ''
        qComment = ''
        qItems = ''
        # question = ''
        questionMain = ''
        rowNums = 0
        qLabel = ''
        qTitle = ''
        self.qChoice = ''
        self.qCol = ''


        for sel in self.view.sel():
            nLs = self.view.split_by_newlines(sel)
            questionLs = []

            for x in nLs:
                questionLs.append(self.view.substr(x).strip())

        for line in questionLs:
            splNum = re.search(r'^\[([0-9]{1,2})\]', line.strip())
            qT = re.search(r'^(?:<)(radio|select|checkbox|number)(?:.*)label=(?:\'|\")([a-zA-Z0-9]\w+)(?:\'|\")(.*)(?:>)', line.strip())
            qCom = re.search(r'<comment>(.*)</comment>', line.strip())
            qCols = re.search(r'^(?:<)(col)(.*)', line.strip())
            qChoices = re.search(r'^(?:<)(choice)(.*)', line.strip())
            qRow = re.search(r'^(?:<)(row)(.*)', line.strip())
            qtitle = re.search(r'<title>(.*)</title>', line.strip())
            if qT:
                # qHead = line + '\n'
                qType = qT.group(1)
                qLabel = qT.group(2)

            elif qCom:
                qComment = line + '\n'
            elif qCols:
                self.qCol = ", cols=True"
                qItems += '  ' + line + '\n'
            elif qChoices:
                self.qChoice = ", choices=True"
                qItems += '  ' + line + '\n'
            elif qRow:
                rowNums += 1
                qItems += '  ' + line + '\n'
            elif splNum:
                splNums = int(splNum.group(1))
            elif qtitle:
                qTitle = line +'\n'

        makeSplitQuestions = make_split_questions(self, qType, splNums, rowNums, qLabel, qComment, qItems, qTitle)
        makeMergeQuestion = question_merge(splNums, qLabel)
        makeOriginalQuestion = make_original_question(self, qType, qLabel, qComment, qItems, qTitle)
        questionMain = makeSplitQuestions + makeMergeQuestion + makeOriginalQuestion

        self.view.replace(edit, sel, questionMain)

class MakeListCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                input = self.view.substr(sel).strip()
                input = fixUniCode(input)
                tag = re.search(r"^\[([a-zA-Z0-9]+)\]", input)
                input = re.sub(r"^\[[a-zA-Z0-9]+\]",'', input)

                if tag is not None:
                    lType = str(tag.group(1))
                else:
                    lType = u"ul"

                input = input.split('\n')
                listI = u"<{0}>\n".format(lType)

                for x in input:
                    if len(x) > 0:
                        listI += u"  <li>{0}</li>\n".format(x)
                listI += u"</{0}>".format(lType)

            self.view.replace(edit,sel,listI)
        except Exception as e:
            print (e)


class CleanCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                input = self.view.substr(sel).strip()
                input = re.sub(r"(<.*?>\[.*?\]<.*?>|\[.*?\])", "", input)
                input = fixUniCode(input)

                self.view.replace(edit,sel, input)
        except Exception as e:
            print (e)


class NoanswerCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()
            printPage = u""
            for sel in sels:
                input = self.view.substr(sel).strip()
                input =  make_labels(input, "na", '\n')

                for x in input:
                    printPage += u"  <noanswer label=\"{label}\">{content}</noanswer>\n".format(label=x[0], content=x[1])

                self.view.replace(edit,sel, printPage)
        except Exception as e:
            print (e)

class AutoSumCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                printPage = 'uses=\"autosum.3\"'
                input = self.view.substr(sel).strip()
                aS = re.search(r"\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]", input)
                items = []
                # Wouldn't let me enumerate
                i = 0

                for x in aS.groups():
                    if x != "":
                        if i == 0:
                            preText = "autosum:preText=\"{0}\"".format(aS.group(1))
                            items.append(preText)
                        elif i == 1:
                            postText = "autosum:postText=\"{0}\"".format(aS.group(2))
                            items.append(postText)
                        elif i == 2:
                            totalText = "autosum:sumPreText\"{0}\"".format(aS.group(3))
                            items.append(totalText)
                        elif i == 3:
                            color = "autosum:color=\"{0}\"".format(aS.group(4))
                            items.append(color)
                        elif i == 4:
                            prefill = "autosum:prefill=\"{0}\"".format(aS.group(5))
                            items.append(prefill)
                        elif i == 5:
                            showRemaining = "autosum:showRemaining=\"{0}\"".format(aS.group(6))
                            items.append(showRemaining)
                    i += 1

                for y in items:
                    printPage += " " + y

                self.view.replace(edit,sel, printPage)
        except Exception as e:
            print (e)

class ZachRowsCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                printPage = u""
                input = self.view.substr(sel).strip()
                input =  make_labels(input, "r", ',')

                for x in input:
                    printPage += u"  <row label=\"{label}\">{content}</row>\n".format(label=x[0], content=x[1])

                self.view.replace(edit,sel, printPage)
        except Exception as e:
            print (e)

class AutoRowsCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                printPage = u""
                input = self.view.substr(sel).strip()
                input = fixUniCode(input)
                input =  make_labels(input, "r", '\n')
                for x in input:
                    printPage += u"  <row label=\"{label}\"{extra}>{content}</row>\n".format(label=x[0], extra=x[2], content=x[1].strip())

                self.view.replace(edit,sel,printPage)
        except Exception as e:
            print (e)

class MakeSpecialColsCommand(sublime_plugin.TextCommand):
    def run (self,edit):
        try:

            sels = self.view.sel()
            input = ''
            for sel in sels:
                printPage = u""
                input = self.view.substr(sel).strip()
                input = fixUniCode(input)
                input = make_labels(input, "c", '\n')
                for x in input:
                    if len(x[0]) and len(x[1]):
                        printPage += u"  <col label=\"{label}\"{extra}>{content}</col>\n".format(label=x[0], extra=x[2], content=x[1].strip())

                self.view.replace(edit,sel, printPage)
        except Exception as e:
            print (e)


class UniqueRows(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                printPage = ""
                uniSet = set([])
                input = self.view.substr(sel).strip()
                input = input.split('\n')
                for x in input:
                    x = x.strip()
                    uniSet.add(x)
                for z in uniSet:
                    printPage += z + '\n'


            self.view.replace(edit,sel, printPage)
        except Exception as e:
            print (e)

class HottextRows(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                printPage = u""
                input = self.view.substr(sel).strip()
                input = fixUniCode(input)
                input = re.sub(r"\n([\s]*)\n", r"\n", input)
                rows = input.split()
                label = 1

                for row in rows:
                    if row.startswith('['):
                        found = re.search(r"\[([A-Za-z0-9_]+)\]", row)
                        extra = found.group(1)
                        row = re.sub(r"\[([A-Za-z0-9_]+)\]", "", row)
                        printPage += u"  <row label=\"r{label}\" hottext:prefix_html=\"&lt;{extra}>\">{content}</row>\n".format(label=label, extra=extra, content=row)
                    elif row.endswith(']'):
                        found = re.search(r"\[([A-Za-z0-9_]+)\]", row)
                        extra = found.group(1)
                        row = re.sub(r"\[([A-Za-z0-9_]+)\]", "", row)
                        printPage += u"  <row label=\"r{label}\" hottext:suffix_html=\"&lt;/{extra}>\">{content}</row>\n".format(label=label, extra=extra, content=row)
                    else:
                        printPage += u"  <row label=\"r{label}\">{content}</row>\n".format(label=label, content=row)

                    label += 1

            self.view.replace(edit,sel, printPage)
        except Exception as e:
            print(e)


class makeCustomComment(sublime_plugin.TextCommand):
    def run (self,edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                printPage = u""
                input = self.view.substr(sel).strip()
                input = fixUniCode(input)
                input = re.sub(r"\n+", r"\n", input)
                input = re.sub(r"(^(\()|(\.|\))+$)", r"", input)
                input = "\n<comment>" + str(input) + "</comment>"

            self.view.replace(edit,sel, input)
        except Exception as e:
            print(e)

class InsertColumns(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            sels = self.view.sel()

            for sel in sels:
                printPage = u""
                input = self.view.substr(sel).strip()
                input = fixUniCode(input)
                input = re.sub(r"\n([\s]*)\n", r"\n", input)
                input = input.split('\n')
                x = input[0].strip(']').strip('[').split('-')
                print(x)
                ranges = [int(x[0]), int(x[1])+1]
                for col in range(ranges[0], ranges[1]):
                    if col == int(x[0]):
                        printPage += u"  <col label=\"c{label}\" value=\"{label}\">{content}<br/> {label}</col>\n".format(label=col, content=input[1])
                    elif col == int(x[1]):
                        printPage += u"  <col label=\"c{label}\" value=\"{label}\">{content}<br/> {label}</col>".format(label=col, content=input[2])
                    else:
                        printPage += u"  <col label=\"c{label}\" value=\"{label}\">{label}</col>\n".format(label=col)

                self.view.replace(edit,sel, printPage)
        except Exception as e:
            print(e)

# class Custom(sublime_plugin.TextCommand):
#     def run (self,edit):
#         try:

#             for sel in self.view.sel():
#                 input = self.view.substr(sel).strip()
#                 input = fixUniCode(input)
#                 input = xmltodict.parse(input)
#                 print(input)


#             # self.view.replace(edit,sel, printPage)
#         except Exception as e:
#             print(e)

# class Custom(sublime_plugin.TextCommand):
#     def run (self,edit):
#         try:
#             sels = self.view.sel()

#             for sel in sels:
#                 printPage = u""
#                 input = self.view.substr(sel).strip()
#                 input = fixUniCode(input)
#                 input = re.sub(r"\n([\s]*)\n", r"\n", input)


#             self.view.replace(edit,sel, printPage)
#         except Exception as e:
#             print(e)