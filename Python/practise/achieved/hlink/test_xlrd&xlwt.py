import xlrd

b = xlrd.open_workbook('app_info20160101002457.xls')
s = b.sheet_by_index(0)
values = {}
#print s.
for h in s.hyperlink_list:
    print h.url_or_path
    print h.fcolx
    print h.frowx
    print eval(str(s.cell(h.frowx,h.fcolx)).replace("text:", ""))
    values[eval(str(s.cell(h.frowx,h.fcolx)).replace("text:", ""))] = h.url_or_path
    #print h.lcolx
    #print h.lrowx
    #print h.textmark



from xlwt import *

f=Font()
f.height=2*7
f.name='Verdana'
f.bold=True
f.underline=Font.UNDERLINE_DOUBLE
f.colour_index=4
h_style=XFStyle()
h_style.font=f
w=Workbook()
ws=w.add_sheet('F')
##############

## NOTE: parameters are separatedby semicolon!!!

##############
count = 0
n="HYPERLINK"
keys = values.keys()
while count < len(keys):
    ws.write(count,0, Formula(n+'("' + values[keys[count]] + '";"' + keys[count] + '")'),h_style)
#ws.write_merge(1,1,1,10,Formula(n+'("http://www.irs.gov/pub/irs-pdf/f1000.pdf";"f1000.pdf")'),h_style)
#ws.write_merge(2,2,2,25,Formula(n+'("mailto:roman.kiseliov@gmail.com?subject=pyExcelerator-feedback&Body=Hello,%20Roman!";"pyExcelerator-feedback")'),h_style)
    count += 1
w.save("hyperlinks.xls")

