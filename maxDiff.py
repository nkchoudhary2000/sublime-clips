import sublime
import sublime_plugin, re
          

def make_attrib(self, edit):
  try:
    sels = self.view.sel()
    input = ''
    printPage = ''
    count = 0
    for sel in sels:
      input = self.view.substr(sel)
      input = re.sub("\t+", " ", input)
      input = re.sub("\n +\n", "\n\n", input)
      input = re.sub("\n{2,}", "\n", input)
      input = input.strip().split("\n")
      del input[0]

      for x in range(0,len(input)):
        input[x] = re.sub("^[a-zA-Z0-9]{1,2}[\.:\)][\t]+", "", input[x])

      for x in input:
        printPage += "<row label=\"item%s\">%s</row>\n" % (str(count+1), input[count].strip())
        count += 1
  except Exception as e:
    print (e) 

  return printPage

  #printPage = ''
	# for count in range(1, attribCount+1):
	# 	printPage += "<row label=\"item%s\">Item %s</row>\n" % (count, count)
	# return printPage

def make_res_tag(attribCount):
  printPage = ''
  for count in range(1, attribCount+1):
    printPage += "<res label=\"item%s\">Item %s</res>\n" % (count, count)
  return printPage

def make_loopvar(loopCount):
  printPage = ''
  for count in range(1, loopCount+1):
    printPage += "<looprow label=\"%s\"><loopvar name=\"task\">%s</loopvar></looprow>\n" % (count, count)
  return printPage

def make_maxdiff(qLabel, insertRes, insertLoop, insertAttrib, qRange):
  qQuestion = """
<note>MaxDiff Alternatives Template --Start--</note>
<exec when="init">
def setupMaxDiffFile(fname, fileDelimiter="\\t"):
    try:
        f = open("%s/%s" % (gv.survey.path, fname))
        mdObj = [ line.strip("\\r\\n").split(fileDelimiter) for line in f.readlines() ]
        d = dict( ("v%s_t%s" % (row[0], row[1]), row[2:]) for row in mdObj )
    except IOError:
        d = {}
    return d

def setupMaxDiffItemsA(d, vt, question, parentLabel):
    items = d[vt]

    print "*****STAFF ONLY*****"
    print "Version_Task: %s" % vt
    for r in question.rows:
        r.text = res[ "%s_mditem%s" % (parentLabel, items[r.index]) ]
        print "Item %s: %s" % (r.index+1, items[r.index])
    </exec>
    
    <exec when="init">"""+qLabel+"""_md = setupMaxDiffFile("md_design.dat")</exec>

   """+insertRes+"""


    <quota label=\""""+qLabel+"""_quota" overquota="noqual" sheet=\""""+qLabel+"""_MaxDiff"/>
    
    <number label=\""""+qLabel+"""_Version" size="3" optional="1" verify="range(1,"""+str(qRange)+""")" where="execute">
      <title>"""+qLabel+""" - MaxDiff Version</title>
      <exec>
print p.markers
for x in p.markers:
    if "/"""+qLabel+"""_MaxDiff/ver_" in x:
        """+qLabel+"""_Version.val = int(x.split("_")[-1])
        break
      </exec>
    </number>
    <suspend/>
    
    <exec>p.startTime = timeSpent()</exec>

    <loop label=\""""+qLabel+"""_md_loop" vars="task" randomizeChildren="0">
      <title>"""+qLabel+""" - MaxDiff Loop</title>
      <block label=\""""+qLabel+"""_md_block" randomize="1">

        <radio label=\""""+qLabel+"""_[loopvar: task]" adim="cols" grouping="cols" unique="1" ss:questionClassNames=\""""+qLabel+"""_maxdiff">
          <title>Title update [MDcount]</title>
          <comment>Select one</comment>
          <exec>
setupMaxDiffItemsA( """+qLabel+"""_md, "v%d_t%d" % ("""+qLabel+"""_Version.val, [loopvar: task]), """+qLabel+"""_[loopvar: task], \""""+qLabel+"""\")
p.MDcount = str("""+qLabel+"""_md_loop_expanded.order.index([loopvar: task]-1)+1)
          </exec>

          <col label="best">Most Important</col>
          <col label="worst">Least Important</col>
"""+insertAttrib+"""


<style name="question.header" mode="before">
            <![CDATA[
    <style type="text/css">
    ."""+qLabel+"""_maxdiff tr.maxdiff-header-legend {
        background-color: transparent;
        border-bottom: 2px solid #d9d9d9;
    }
    ."""+qLabel+"""_maxdiff tr.maxdiff-header-legend th.legend {
        background-color: transparent;
        border: none;
    }
    ."""+qLabel+"""_maxdiff tr.maxdiff-row td.element {
        border-left: none;
        border-right: none;
        border-top: none;
        border-bottom: 1px solid #d9d9d9;
        text-align: center;
    }
    ."""+qLabel+"""_maxdiff tr.maxdiff-row th.row-legend {
        background-color: transparent;
        border-left: none;
        border-right: none;
        border-top: none;
        border-bottom: 1px solid #d9d9d9;
        text-align: center;
    }
    </style>
            ]]>
</style>
 
<style name="question.top-legend">
            <![CDATA[
\@if ec.simpleList
    $(legends)
\@else
    <$(tag) class="maxdiff-header-legend row row-col-legends row-col-legends-top ${"mobile-top-row-legend " if mobileOnly else ""}${"GtTenColumns " if ec.colCount > 10 else ""}colCount-$(colCount)">
        ${"%s%s" % (legends.split("</th>")[0],"</th>")}
       $(left)
        ${"%s%s" % (legends.split("</th>")[1],"</th>")}
    </$(tag)>
    \@if not simple
  </tbody>
  <tbody>
    \@endif
\@endif
            ]]>
</style>
 
<style name="question.row">
            <![CDATA[
\@if ec.simpleList
    $(elements)
\@else
    <$(tag) class="maxdiff-row row row-elements $(style) colCount-$(colCount)">
        ${"%s%s" % (elements.split("</td>")[0],"</td>")}
        $(left)
        ${"%s%s" % (elements.split("</td>")[1],"</td>")}
    </$(tag)>
\@endif
            ]]>
</style>
  </radio>
      </block>
      
      """+insertLoop+"""
    
    </loop>
    
    <float label=\""""+qLabel+"""_Timer" size="15" where="execute">
      <title>"""+qLabel+""" - MaxDiff Timer (Minutes)</title>
      <exec>"""+qLabel+"""_Timer.val = (timeSpent() - p.startTime) / 60.0</exec>
    </float>
    
    <note>MaxDiff Alternatives Template --End--</note>
  """
  return qQuestion

def make_question(self, edit, qLabel, qRange, qAttribCount, qLoopCount):
  insertRes = make_res_tag(qAttribCount)
  insertLoop = make_loopvar(qLoopCount)
  insertAttrib = make_attrib(self, edit)
  qQuestion = make_maxdiff(qLabel, insertRes, insertLoop,insertAttrib, qRange)
  sels = self.view.sel()
  for sel in sels:
    self.view.replace(edit,sel, qQuestion)

  return qQuestion



class MaxDiffCommand(sublime_plugin.TextCommand):
  def run(self, edit):
  	for sel in self.view.sel():
  		qListLine = self.view.split_by_newlines(sel)
  		qListString = [self.view.substr(x).strip() for x in qListLine]

  	print (qListLine[0])
  	print (qListString[0])
  	qListAttrib = qListString[0].split('-')
  	qLabel = str(qListAttrib[0])
  	qRange = int(qListAttrib[1])
  	qLoopCount = int(qListAttrib[2])
  	qAttribCount = int(qListAttrib[3])
  	make_question(self, edit, qLabel, qRange, qAttribCount, qLoopCount)