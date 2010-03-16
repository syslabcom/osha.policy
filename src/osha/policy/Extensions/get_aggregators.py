from slc.aggregation.interfaces import IAggregator
from p4a.subtyper.interfaces import IPortalTypedFolderishDescriptor

def run(self):
	""" """
	aggregators = []
	ls = self.portal_catalog(portal_type='Folder') # , Language='all')
	for l in ls:
		try:
			o = l.getObject()
		except:
			continue

		if IAggregator.providedBy(o):
			if o.absolute_url() in ['http://deimos7:5040/osha/portal/en/good_practice/sector/healthcare/faq']:
				import pdb; pdb.set_trace()
			aggregators.append(o.absolute_url())

	return '\n'.join(aggregators)


# FAQ aggregators:
# =============================
# http://osha.europa.eu/en/general-faq
# http://osha.europa.eu/en/good_practice/sector/agriculture/faq - does not exist
# http://osha.europa.eu/en/good_practice/sector/construction/faq - does not exist
# http://osha.europa.eu/en/good_practice/sector/education/faq - does not exist
# http://osha.europa.eu/en/good_practice/sector/fisheries/faq - does not exist
# http://osha.europa.eu/en/good_practice/sector/healthcare/faq - does not exist
# http://osha.europa.eu/en/good_practice/topics/accident_prevention/faq - does not exist
# http://osha.europa.eu/en/good_practice/topics/dangerous_substances/faq -does not exist
# http://osha.europa.eu/en/priority_groups/disability/faq.php
# http://osha.europa.eu/en/topics/ds/oel/faq - Had no keywords, I changed that to search for 'dangerous_substances'
# http://osha.europa.eu/en/topics/msds/FAQs
