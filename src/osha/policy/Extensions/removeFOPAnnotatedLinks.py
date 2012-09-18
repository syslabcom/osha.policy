import codecs


def run(self):
    request = self.REQUEST
    response = self.REQUEST.response

    # Don't touch these ones
    blacklist = [ "sv", "fi", "en",]
    do_delete = 0

    country = "finland"

    log_file = codecs.open(
        "/srv/oshawebdev/"+country+".log", "a", "utf-8")

    fop = self.portal.ro.oshnetwork["focal-points"][country].index_html
    translations = fop.getTranslations()
    fop_links = fop.annotatedlinklist


    for i in translations.keys():
        if i not in blacklist:
            trans_fop = translations[i][0]
            if trans_fop.annotatedlinklist != fop_links:
                diff = []
                for key in trans_fop.annotatedlinklist:
                    if key not in fop_links:
                        diff.append(key)
                response.write(
                    "%s has different links: %s\n" %(i, diff))
            else:
                response.write("same same: %s\n" %(i))
            if do_delete:
                response.write("Deleted links from %s\n" %i)
                log_file.write("'%s', %s\n" %(i, trans_fop.annotatedlinklist))
                trans_fop.annotatedlinklist = ()
