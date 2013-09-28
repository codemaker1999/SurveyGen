# -*- coding: cp1252 -*-
#=========================================================================================
# Imports
from reportlab.platypus.tables import Table, TableStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Spacer, PageBreak, Image
from PIL import Image as PILImage
from reportlab.lib.colors import toColor
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.units import inch,mm
from reportlab.lib.pagesizes import letter
import os, sqlite3, hashlib
from meade.qrcode import zxing # see other repo
#=========================================================================================
# Init
PAGES = 2
styles = getSampleStyleSheet()

styleBT = styles["BodyText"]
styleBT.fontSize = 9

styleBold = styles["Normal"]
styleBold.fontName = 'Helvetica-Bold'
styleBold.fontSize = 9
styleBold.alignment = TA_CENTER

#=========================================================================================
# Functions
def p(text,style=styleBT):
    'Quickly make text into a Paragraph'
    return Paragraph(text, style)

def SQL_to_2D_list(fn):
    '''
    Convert a SQLITE db into a 2D list

    Sample output
    [[1 , 'I do work', 'SA','A','N','D','SD'],
     ['', '',          '',  '', '', '', ''  ],
     ['', '',          '',  '', '', '', ''  ],
     [2 , 'I get money', 'SA','A','N','D','SD'],
     ['', '',            '',  '', '', '', ''  ],
     ['', '',            '',  '', '', '', ''  ],
     ...]

    where the question text column has rowspan of 2 for each question
    '''
    # Open SQLITE3 DB
    conn = sqlite3.connect(fn)
    cur = conn.cursor()
    #
    answer_cells = ['SA','A','D','SD','DNK']
    blank_row = ['','','','','','','']
    global styleBT
    table = []
    for row in cur.execute('SELECT * FROM questions ORDER BY num'):
        # Without putting text in a Paragraph, it will not wrap
        table.append( [row[0], p(row[1])] + answer_cells )
        table.append( blank_row )
        table.append( blank_row )
    conn.close()
    return table

def SQL_to_table(fn):
    'Convert a SQLITE db to a table object'
    data = SQL_to_2D_list(fn)
    # add blank column to the end for clean splitting between pages
    for i in range(len(data)):
        newrow = data[i] + ['']
        data[i] = newrow
    # Style Sheet
    style=[('VALIGN',(0,0),(-1,-1),'TOP'),
           ('ALIGN',(0,0),(0,-1),'CENTER'),#number col
           ('VALIGN',(0,0),(0,-1),'MIDDLE'),#number col
           ('ALIGN',(2,0),(-1,-1),'CENTER'),#answer col
           ('VALIGN',(2,0),(-1,-1),'MIDDLE'),#answer col
           ('RIGHTPADDING',(0,0),(-1,-1),5),
           ('LEFTPADDING',(0,0),(-1,-1),5),
           ('TOPPADDING',(0,0),(-1,-1),1),
           ('BOTTOMPADDING',(0,0),(-1,-1),1)]
    # special styles
    for i in range(0,len(data),3):
        style.append( ('SPAN',(-1,i),(-1,i+2)) ) # merge blank column rows
        style.append( ('SPAN',(1,i),(1,i+1)) ) # merge text rows
        style.append( ('GRID',(1,i),(-2,i+1),1,colors.black) ) # add grid lines
        style.append( ('BOX',(0,i),(0,i+1),1,colors.black) ) # grid around numbers
        style.append( ('BOX',(0,i+2),(-2,i+2),1,colors.black) ) # grid around separator
        style.append( ('TOPPADDING',(0,i+2),(-2,i+2),29) ) # Leave space for comments
    t = Table(data, colWidths=(25,355,26,26,26,26,26,1))
    t.setStyle(TableStyle(style))
    return t

def misc_questions():
    'Extra table with misc questions'
    # Left Table
    r1 = [p('How long have you been with this organization?',style=styleBold),'']
    r2 = [p('Between 0-5 years'),'']
    r3 = [p('Between 6-10years'),'']
    r4 = [p('Between 11-15 years'),'']
    r5 = [p('More than 15 years'),'']
    r6 = ['','']
    r7 = ['','']
    r8 = ['','']
    r9 = ['','']
    r10= ['','']
    r11= ['','']
    r12= ['','']
    r13= ['','']
    r14= ['','']
    r15= ['','']
    # Spacer Column
    r1  += ['']
    r2  += ['']
    r3  += ['']
    r4  += ['']
    r5  += ['']
    r6  += ['']
    r7  += ['']
    r8  += ['']
    r9  += ['']
    r10 += ['']
    r11 += ['']
    r12 += ['']
    r13 += ['']
    r14 += ['']
    r15 += ['']
    # Right Table
    r1  += [p('Please select your department.',style=styleBold),'']
    r2  += [p('dept1'),'']
    r3  += [p('Emergency Services'),'']
    r4  += [p('Health Unit'),'']
    r5  += [p('HR/Clerks Office'),'']
    r6  += [p('dept2'),'']
    r7  += [p('dept3'),'']
    r8  += [p('dept4'),'']
    r9  += [p('Information Technology'),'']
    r10 += [p('Library Services'),'']
    r11 += [p('Planning and Development'),'']
    r12 += [p('Property Services'),'']
    r13 += [p('Public Works'),'']
    r14 += [p('Social Services'),'']
    r15 += [p('Treasury'),'']
    #
    data = [r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12,r13,r14,r15]
    style = [('SPAN',(0,0),(1,0)),#left
             ('SPAN',(3,0),(4,0)),#right
             ('BOX',(0,0),(1,0),1,colors.black),#left
             ('BOX',(3,0),(4,0),1,colors.black),#right
             ('GRID',(0,1),(1,4),1,colors.black),#left
             ('GRID',(3,1),(4,-1),1,colors.black),]#right
    t = Table(data,colWidths=(200,22,80,160,22))
    t.setStyle(style)
    return t

def legend():
    'Description of answer abreviations'
    data = [[p('Strongly Agree'),'SA'],
            [p('Agree'),'A'],
            [p('Disagree'),'D'],
            [p('Strongly Disagree'),'SD'],
            [p('Do Not Know / Neutral'), 'DNK']]
    style = [('BACKGROUND',(0,0),(1,0),'rgb(215,255,200)'),
             ('BACKGROUND',(0,1),(1,1),'rgb(200,215,255)'),
             ('BACKGROUND',(0,2),(1,2),'rgb(255,250,180)'),
             ('BACKGROUND',(0,3),(1,3),'rgb(255,200,200)'),
             ('BACKGROUND',(0,4),(1,4),'rgb(235,240,250)'),
             ('GRID',(0,0),(-1,-1),1,colors.black),
             ('BOX',(0,0),(-1,-1),2,colors.black)]
    t = Table(data,colWidths=(130,50))
    t.setStyle(style)
    return t

def addPageNumber(canvas, doc):
    'Add the page number'
    page_num = canvas.getPageNumber() % PAGES
    if page_num == 0: page_num = PAGES
    text = "Page #%d"%page_num
    canvas.drawCentredString(letter[0]/2.0, 20*mm, text)

#=========================================================================================
# Run
def addSurvey(story, ID):
    '''
    Add a survey with unique identifier <ID> to the story
    ID is an 8-digit, alpha-numeric string, case-insensitive
    '''
    #logo
    im_w,im_h = 600,425
    w,h  =  im_w/4.0, im_h/4.0
    logo = Image('logo.png',width=w,height=h)
    story.append( logo )
    story.append( Spacer(1,6*mm) )
    # Title
    text = p('<font size=12>A Survey Title</font>',styleBold)
    story.append( text )
    story.append( Spacer(1,6*mm) )
    #legend / key
    table = legend()
    story.append(table)
    #info
    text = p('<font size=7>*Leave comments in the space below each question</font>')
    story.append(text)
    story.append(Spacer(1,1*mm))
    #main table
    table = SQL_to_table('survey.db')
    story.append(table)
    story.append(PageBreak())
    #info
    story.append( p('Additional Questions:') )
    story.append(Spacer(1,2*mm))
    #other questions
    table = misc_questions()
    story.append(table)
    story.append(Spacer(1,inch))
    #info
    text = p('<font size=8>'+\
             'If you have further comments please feel free to write on the back of any page.<br/>'+\
             'All comments will be appreciated and taken into consideration.'+\
             '</font>',style=styleBold)
    story.append(text)
    story.append(Spacer(1,0.5*inch))
    #info
    text = p('<font size=12>'+\
             'Thank you for your participation in this survey!'
             '</font>',style=styleBold)
    story.append(text)
    story.append(Spacer(1,0.8*inch))
    #QR Image
    #zxing.genQR(ID,outputDir='QRcodes')
    fn=os.path.join('QRcodes',ID+'.png')
    qr_im = Image(fn,100,100)
    story.append( qr_im )
    #QR String
    text = p('<font size=14>'+ID+'</font>',styleBold)
    story.append(text)
    return story
    
if __name__ == '__main__':
    #
    # Get IDs
    #
    IDlist = []
    with open('IDs.txt','r') as f:
        for ID in f.readlines():
            IDlist.append(ID.strip())
    IDs = iter(IDlist)
    #
    # Make Document
    #
    fn = 'Survey.pdf'
    doc = SimpleDocTemplate(fn, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    #
    # Add pages
    #
    verbose = True
    story = []
    ID    = IDs.next()
    n     = 1
    print 'Preparing pages...'
    while True:
        #if n > 3: break #testing
        story = addSurvey( story, ID )
        n += 1
        try:
            ID = IDs.next()
        except StopIteration:
            break
        else:
            story.append( PageBreak() )
    #
    # Build Document
    #
    print '\nBuilding Document...'
    doc.build(story, onFirstPage=addPageNumber, onLaterPages=addPageNumber)
    print '\nDone'
