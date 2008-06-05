from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from StringIO import StringIO
from reportlab import rl_config
from reportlab.platypus.flowables import PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, Frame
import os, tempfile


import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = 0
from DateTime import DateTime

def generatePDF(self, company="European Agency for Safety and Health at Work", language='en', firstname='', lastname='', checkboxes={}, usePDFTK=0):
    language = language.lower()
    

    
    if language not in ['bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi', 'fr', 'hu', 'it', 'lt', 'lv', 'mt', 'nl', 'pl', 'ro', 'pt', 'sk', 'sl', 'sv']:
        language = "en"

    # get translation-service
    ptt = self.Control_Panel.TranslationService
    ptt_domain = 'osha_ew'
    #year = str(DateTime().year())
    year = "2008"
#    print "WEBCHARTER:",year, "in", language

    # create a canvas and set metadata
    acknowledge = StringIO()
    my_canvas = canvas.Canvas(acknowledge, pagesize=landscape(A4))
    my_canvas.setTitle('Charter of the Healthy Workplaces campaign')
    my_canvas.setAuthor('European Agency for Safety and Health at Work')
    my_canvas.setSubject('Charter of the Healthy Workplaces campaign')

    # register the font for writing company, name and actions
    arial =  INSTANCE_HOME + '/Products/OSHA/data/arial.ttf'
    pdfmetrics.registerFont( TTFont('Arial', arial) )
    arial_bold =  INSTANCE_HOME + '/Products/OSHA/data/arialbd.ttf'
    pdfmetrics.registerFont( TTFont('ArialBold', arial_bold) )
    arial_italic =  INSTANCE_HOME + '/Products/OSHA/data/ariali.ttf'
    pdfmetrics.registerFont( TTFont('ArialItalic', arial_italic) )
    arial_bi =  INSTANCE_HOME + '/Products/OSHA/data/arialbi.ttf'
    pdfmetrics.registerFont( TTFont('ArialBoldItalic', arial_bi) )
    arial_nb =  INSTANCE_HOME + '/Products/OSHA/data/arialnb.ttf'
    pdfmetrics.registerFont( TTFont('ArialNarrowBold', arial_nb) )

    # get the frontimage and write it to the canvas
    charterfilename = "charter_hw2008-%s.jpg"
    frontfile = getattr(self.charter_img, charterfilename % language, None)
    # Fallback to English
    if not frontfile:
        frontfile = getattr(self.charter_img, charterfilename % 'en')
    frontdata = str(frontfile.data)
    frontfile =StringIO(frontdata)
    frontimage = ImageReader(frontfile)
    my_canvas.drawImage(frontimage, 0 , 0, 29.7*cm, 21*cm)

#    # print campaign-slogan
    msg_id = 'campaign_slogan_'+year
    u_campaign_slogan = ptt.utranslate(ptt_domain, msg_id, target_language=language)
#    campaign_slogan = u_campaign_slogan.encode('utf-8')
#    print campaign_slogan, type(campaign_slogan)
#    x =  4.5 * cm
#    y = 18.8 * cm
#    if my_canvas.stringWidth(campaign_slogan, 'ArialBoldItalic', 30) > 300:
#        y = 18.5 * cm
#    my_canvas.setFont('ArialBoldItalic', 30)
#    my_canvas.setFillColorRGB(0.5, 0.5, 0.5)
#    my_canvas.drawString(x+(0.07*cm), y-(0.05*cm), campaign_slogan)
#    my_canvas.setFillColorRGB((252.0/255), (176.0/255), (61.0/255))
#    my_canvas.drawString(x, y, campaign_slogan)
#    print " +- set campaign slogan"#, campaign_slogan
#
    # prepare the replacement-mapping for the coming u_translations
    mapping = {'campaign_slogan':u_campaign_slogan, 'year':year}
#    print " +--Mapping:", mapping
#
#
#    # print EW-slogan
#    # if the Campaign-Slogan is taller than the half of the page-width
#    # then print the EW-Slogan above the Campaign slogan instead of the same height
#    ew_slogan = ptt.utranslate(ptt_domain, 'ew_slogan', mapping=mapping, target_language=language)
#    ew_slogan = ew_slogan.encode('utf-8')
#    x = 28.55* cm
#    y = 19.2 * cm
#    if my_canvas.stringWidth(campaign_slogan, 'ArialBoldItalic', 30) > 300:
#        y = 19.6 * cm
#    my_canvas.setFont('ArialNarrowBold', 14)
#    my_canvas.setFillColorRGB(0, 0, 0)
#    my_canvas.drawRightString(x, y, ew_slogan)
#    print " +- set EW slogan"
#
    # print headline
    certificate_title = ptt.utranslate(ptt_domain, 'certificate_title_'+year, target_language=language)
    certificate_title = certificate_title.encode('utf-8')
    x = 14.85 * cm
    y = 16.6 * cm
    my_canvas.setFont('Arial', 30)
    my_canvas.drawCentredString(x, y, certificate_title.upper())
    print " +- set Headline"#, certificate_title

    # print first subline
    certificate_for = ptt.utranslate(ptt_domain, 'certificate_for_'+year, mapping=mapping, target_language=language)
    certificate_for = certificate_for.encode('utf-8')
    x = 14.85 * cm
    y = 15.0 * cm
    my_canvas.setFont('Arial', 16)
    my_canvas.drawCentredString(x, y, certificate_for)
    print " +- set first subline"#, certificate_for

    # print company name
    x = 14.85 * cm
    y = 13.0 * cm
    my_canvas.setFont('Arial', 30)
    my_canvas.drawCentredString(x, y, company)
    print " +- set comany name"#, company
#
    # print contribution headline
    style = ParagraphStyle(
            name='ContributionHeadline',
            fontName='Arial',
            fontSize=16,
            spaceAfter=6,
            leading=18,
            alignment=1
        )

    lines = []
    contribution_headline = ptt.utranslate(ptt_domain, 'contribution_headline_'+year, mapping=mapping, target_language=language)
    contribution_headline = contribution_headline.encode('utf-8')
    lines.append( Paragraph(contribution_headline, style) )
    cFrame = Frame(2*cm, 9.0*cm, 25.7*cm, 3*cm)
    cFrame.addFromList(lines, my_canvas)
    
    # Director's signature
    director_name = "Jukka Takala,"
    director_name = director_name.encode('utf-8')
    director_indentifiyier = ptt.utranslate(ptt_domain, 'director', mapping=mapping, target_language=language)
    director_indentifiyier = director_indentifiyier.encode('utf-8')
    
    style = ParagraphStyle(
            name='ContributionHeadline',
            fontName='Arial',
            fontSize=16,
            spaceAfter=6,
#            leading=18,
            alignment=0
        )
    lines = []
    lines.append(Paragraph(director_name, style))
    lines.append(Paragraph(director_indentifiyier, style))
    dFrame = Frame(3.5*cm, 3.7*cm, 5*cm, 3*cm)
    dFrame.addFromList(lines, my_canvas)
    
    
#    contribution_subline = ptt.utranslate(ptt_domain, 'contribution_subline', mapping=mapping, target_language=language)
#    contribution_subline = contribution_subline.encode('utf-8')
#    if contribution_subline.find('${campaign_slogan}') > -1:
#        contribution_subline = contribution_subline.replace('${campaign_slogan}', campaign_slogan)
#    lines.append( Paragraph(contribution_headline, style) )
#    lines.append( Paragraph(contribution_subline, style) )
#
#    cFrame = Frame(2*cm, 11*cm, 25.7*cm, 2.5*cm)
#    cFrame.addFromList(lines, my_canvas)
#    print " +- set contribution headline"#, contribution_headline, contribution_subline
#
#    # print actions of subscriber
#    style = ParagraphStyle(
#            name='CustomActivities',
#            fontName='Arial',
#            fontSize=12,
#            bulletFontName='Symbol',
#            bulletFontSize=12,
#            bulletIndent=5,
#            leftIndent = 20,
#            leading=15
#        )
#    x_left = 2.1 * cm
#    y_left = 1.4 * cm
#    aw_left = 12.3 * cm
#    ah_left = 10 * cm
#
#    x_right = 15.5 * cm
#    y_right = y_left
#    aw_right = aw_left
#    ah_right = ah_left
#
#    act_keys= checkboxes.keys()
#    act_keys.sort()
#    frame_left = Frame(x_left, y_left, aw_left, ah_left, 0 ,0 ,0 ,0)
#    frame_right = Frame(x_right, y_right, aw_right, ah_right, 0, 0, 0, 0)
#    act_left = []
#    act_right = []
#    idx = 0
#    print "act_keys:", act_keys
#    for k in act_keys:
#        print "key:",  k
#        act = "<bullet/>%s" % (checkboxes[k])
#        P = Paragraph(act, style, '\267')
#        if idx % 2:
#            act_left.append(P)
#        else:
#            act_right.append(P)
#        idx = idx + 1
#
#    frame_left.addFromList(act_left, my_canvas)
#    frame_right.addFromList(act_right, my_canvas)
#    print " +- set subscribed actions"

#    # print name of subscriber
#    x = 14.85 * cm
#    y = 3.5 * cm
#    font_size_name = 14
#    name = "%s %s" %(firstname, lastname)
#    my_canvas.setFont('Arial', font_size_name)
#    my_canvas.drawCentredString(x, y, name)
#    print " +- set subscriber name"
    
    # ***** FALLBACK-SOLUTION UNTIL PDFTK IS AVAILABLE *******
    if usePDFTK == 0:
        print "Set Charter-Image as second page w/o PDFTK"
        # set the webcharter-image as second page
        chartername = "charter_hw2008-%s.jpg" 
        charterfile = getattr(self.charter_img, chartername % language, None)
        # Fallback to English
        if not charterfile:
            charterfile = getattr(self.charter_img, chartername % 'en')
        print "have charterfile:", [charterfile]
        charterdata = str(charterfile.data)
        charterdata = StringIO(charterdata)
        charterimage = ImageReader(charterdata)

##        my_canvas.drawImage(charterimage, 0 , 0, 29.7*cm, 21*cm)
        my_canvas.showPage()
        my_canvas.save()
        return acknowledge.getvalue()


    # ****** NEEDS PDFTK SUPPORT ********
    if usePDFTK == 1:
        print "Start merging with PDFTK"
        # merge the webcharter and the acknowledge PDFs
        chartername = "charter_hw2008-%s.jpg" 
        charterfile = getattr(self.charter_img, chartername % language, None)
        # Fallback to English
        if not charterfile:
            charterfile = getattr(self.charter_img, chartername % 'en')
        print "got webcharter:", chartername

        # generate temp-files of both PDFs
        tmp_charter_file = tempfile.mkstemp(suffix='.pdf')
        charter_fd = open(tmp_charter_file[1], 'w')
        charter_fd.write(str(charterfile.data))
        #charter_fd.close()
        print "wrote charter-temp", tmp_charter_file[1]

        # save the acknowledge
        my_canvas.save()
        tmp_ack_file = tempfile.mkstemp(suffix='.pdf')
        ack_fd = open(tmp_ack_file[1], 'w')
        ack_fd.write(acknowledge.getvalue())
        #ack_fd.close()
        print "wrote ack-temp", tmp_ack_file[1], len(acknowledge.getvalue())

        # merge PDFs with PDF-Toolkit
        statement = 'pdftk %s %s cat output -' % (tmp_charter_file[1], tmp_ack_file[1])
        print "system-call:", statement
        ph = os.popen(statement)
        data = StringIO()
        data.write(ph.read())
        ph.close()
        print "output len:", len(data.getvalue())

        os.remove(tmp_charter_file[1])
        os.remove(tmp_ack_file[1])

        print "==================================="
        return data.getvalue()
