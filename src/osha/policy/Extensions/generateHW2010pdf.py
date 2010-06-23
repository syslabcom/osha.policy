import os, tempfile
from StringIO import StringIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.colors import red, black
from reportlab.lib.enums import TA_CENTER
import reportlab.rl_config

reportlab.rl_config.warnOnMissingFontGlyphs = 0

def generatePDF(self, 
        company="European Agency for Safety and Health at Work", 
        language='en', 
        firstname='', 
        lastname='', 
        checkboxes={}, 
        usePDFTK=0):
        
    language = language.lower()
    
    if language not in [
                'bg', 'cs', 'da', 'de', 
                'el', 'en', 'es', 'et', 
                'fi', 'fr', 'hu', 'it', 
                'lt', 'lv', 'mt', 'nl', 
                'pl', 'ro', 'pt', 'sk', 
                'sl', 'sv']:
        language = "en"

    # get translation-service
    from Products.PlacelessTranslationService import getTranslationService
    ptt = getTranslationService()
    ptt_domain = 'osha_ew'
    year = "2010"

    # create a canvas and set metadata
    acknowledge = StringIO()
    my_canvas = canvas.Canvas(acknowledge, pagesize=A4)
    my_canvas.setTitle('Charter of the Healthy Workplaces campaign')
    my_canvas.setAuthor('European Agency for Safety and Health at Work')
    my_canvas.setSubject('Charter of the Healthy Workplaces campaign')

    # register the font for writing company, name and actions
    arial =  INSTANCE_HOME + '/../../data/arial.ttf'
    pdfmetrics.registerFont( TTFont('Arial', arial) )
    arial_bold =  INSTANCE_HOME + '/../../data/arialbd.ttf'
    pdfmetrics.registerFont( TTFont('ArialBold', arial_bold) )
    arial_italic =  INSTANCE_HOME + '/../../data/ariali.ttf'
    pdfmetrics.registerFont( TTFont('ArialItalic', arial_italic) )
    arial_bi =  INSTANCE_HOME + '/../../data/arialbi.ttf'
    pdfmetrics.registerFont( TTFont('ArialBoldItalic', arial_bi) )
    arial_nb =  INSTANCE_HOME + '/../../data/arialnb.ttf'
    pdfmetrics.registerFont( TTFont('ArialNarrowBold', arial_nb) )

    # get the frontimage and write it to the canvas
    charterfilename = "charter_hw2010_%s.jpg"
    frontfile = getattr(self.charter_img, charterfilename % language, None)
    # Fallback to English
    if not frontfile:
        frontfile = getattr(self.charter_img, charterfilename % 'en')
    frontdata = str(frontfile.data)
    frontfile =StringIO(frontdata)
    frontimage = ImageReader(frontfile)
    # my_canvas.drawImage(frontimage, 0 , 0, 87.5*cm, 123.8*cm)
    my_canvas.drawImage(frontimage, 0 , 0, 21*cm, 29.7*cm)

    msg_id = 'campaign_name_'+year
    u_campaign_name = ptt.translate(
                                domain=ptt_domain, 
                                msgid=msg_id, 
                                target_language=language, 
                                context=self
                                )
    x = 10.4 * cm
    y = 28 * cm
    my_canvas.setFont('ArialBold', 20)
    my_canvas.drawCentredString(x, y, u_campaign_name.upper())
    print " +- set Heading"
    mapping = {'campaign_slogan':u_campaign_name, 'year':year}

    msg_id = 'campaign_slogan_'+year
    u_campaign_slogan = ptt.translate(
                                domain=ptt_domain, 
                                msgid=msg_id, 
                                target_language=language, 
                                context=self
                                )
    x = 10.5 * cm
    y = 26.3 * cm
    my_canvas.setFont('ArialBold', 17)
    my_canvas.setFillColor(red)
    my_canvas.drawCentredString(x, y, u_campaign_slogan.upper())
    print " +- set slogan"
    mapping = {'campaign_slogan':u_campaign_slogan, 'year':year}
        
    # print first subline
    certificate_for = ptt.translate(domain=ptt_domain, 
                                    msgid='certificate_for_'+year, 
                                    mapping=mapping, 
                                    target_language=language,
                                    context=self)


    certificate_title = ptt.translate(
                                domain=ptt_domain, 
                                msgid='certificate_title_'+year, 
                                target_language=language, 
                                context=self
                                )
    x = 10.4 * cm
    y = 22.5 * cm
    my_canvas.setFont('Arial', 32)
    my_canvas.setFillColor(black)
    my_canvas.drawCentredString(x, y, certificate_title.upper())
    print " +- set Headline"#, certificate_title
    mapping = {'campaign_slogan':u_campaign_slogan, 'year':year}
        
    # print first subline
    certificate_for = ptt.translate(domain=ptt_domain, 
                                    msgid='certificate_for_'+year, 
                                    mapping=mapping, 
                                    target_language=language,
                                    context=self)
    certificate_for = certificate_for.encode('utf-8')
    x = 10.4 * cm
    y = 21.5 * cm
    my_canvas.setFont('Arial', 18)
    my_canvas.drawCentredString(x, y, certificate_for)
    print " +- set first subline"#, certificate_for

    # print company name
    x = 10.4 * cm
    y = 16 * cm
    width, height = A4
    width -= 5 * cm
    height = 10 * cm

    style = ParagraphStyle(
            name='companyName', 
            fontName='Arial', 
            fontSize=32, 
            leading=34, 
            alignment=TA_CENTER)

    P = Paragraph(company, style)
    wi, he = P.wrap(width, height)
    P.drawOn(my_canvas, x - wi/2, y - he/2)
    print " +- set company name"#, company

    style = ParagraphStyle(
            name='ContributionHeadline',
            fontName='Arial',
            fontSize=18,
            spaceAfter=0,
            leading=22,
            alignment=1
        )

    lines = []
    contribution_headline = ptt.translate(domain=ptt_domain, 
                                          msgid='contribution_headline_'+year, 
                                          mapping=mapping, 
                                          target_language=language,
                                          context=self)

    contribution_headline = contribution_headline.encode('utf-8')
    lines.append( Paragraph(contribution_headline, style) )
    cFrame = Frame(3*cm, 10*cm, 15*cm, 3*cm)
    cFrame.addFromList(lines, my_canvas)
    
    # Director's signature
    director_name = "Jukka Takala,"
    director_name = director_name.encode('utf-8')
    director_indentifier = ptt.translate(domain=ptt_domain, 
                                           msgid='director_'+year, 
                                           mapping=mapping, 
                                           target_language=language,
                                           context=self)
    director_indentifier = director_indentifier.encode('utf-8')
    
    style = ParagraphStyle(
            name='ContributionHeadline',
            fontName='Arial',
            fontSize=16,
            spaceAfter=6,
            alignment=0
        )
    lines = []
    lines.append(Paragraph(director_name, style))
    style = ParagraphStyle(
            name='ContributionHeadline',
            fontName='Arial',
            fontSize=14,
            spaceAfter=6,
            alignment=0,
            leading=16
        )
    lines.append(Paragraph(director_indentifier, style))
    dFrame = Frame(0.8*cm, 5*cm, 20*cm, 3*cm)
    dFrame.addFromList(lines, my_canvas)
    
    
    # ***** FALLBACK-SOLUTION UNTIL PDFTK IS AVAILABLE *******
    if usePDFTK == 0:
        print "Set Charter-Image as second page w/o PDFTK"
        # set the webcharter-image as second page
        chartername = "charter_hw2010_%s.jpg" 
        charterfile = getattr(self.charter_img, chartername % language, None)
        # Fallback to English
        if not charterfile:
            charterfile = getattr(self.charter_img, chartername % 'en')
        print "have charterfile:", [charterfile]
        charterdata = str(charterfile.data)
        charterdata = StringIO(charterdata)
        charterimage = ImageReader(charterdata)
        my_canvas.showPage()
        my_canvas.save()
        return acknowledge.getvalue()

    # ****** NEEDS PDFTK SUPPORT ********
    if usePDFTK == 1:
        print "Start merging with PDFTK"
        # merge the webcharter and the acknowledge PDFs
        chartername = "charter_hw2010_%s.jpg" 
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
