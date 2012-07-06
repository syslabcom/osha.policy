# set default_output_type = "text/html" on content which has it set
# to "text/x-html-safe". This caused getText to transform the raw body
# to content which included extra escaped html, refs #5378

from logging import getLogger

import transaction
from zope.app.component.hooks import getSite

logger = getLogger('osha.policy/set_text_field_output_type')


def main(self):
    portal = getSite()
    pc = portal.portal_catalog

    problem_fields = {
        'Blog Entry': ['text'],
        'CallForContractors': ['text'],
        'Document': ['text'],
        'Event': ['text'],
        'FormFolder': ['formPrologue',
                       'formEpilogue'],
        'FormThanksPage': ['thanksPrologue',
                           'thanksEpilogue',
                           'noSubmitMessage'],
        'HelpCenterFAQ': ['text'],
        'News Item': ['text'],
        'OSH_Link': ['text'],
        'PressContact': ['text'],
        'PressRelease': ['text'],
        'PressRoom': ['text'],
        'Provider': ['description'],
        'PublicJobVacancy': ['text'],
        'RALink': ['text'],
        'RichDocument': ['text'],
        'SPSeminar': ['summary',
                      'conclusions',
                      'furtherActions'],
        'SPSpeaker': ['biography'],
        'SPSpeech': ['text'],
        'Scenario': ['problem',
                     'solution',
                     'note'],
        'Topic': ['text']}

    for portal_type in problem_fields.keys():
        query = {"portal_type" : portal_type}

        results = pc._cs_old_searchResults(query)
        logger.info(
            'Found %d results for type: %s' % (len(results), portal_type))
        results = pc.searchResults(query)
        things_with_output_type = {}
        broken_brains = []
        for count, brain in enumerate(results):
            try:
                obj = brain.getObject()
            except Exception, e:
                broken_brains.append("%s: %s" %(brain.getPath(), e))
                continue

            for field in problem_fields[portal_type]:
                text_field = obj.Schema().getField(field)
                if (text_field
                    and hasattr(text_field, "default_output_type")
                    and text_field.default_output_type == "text/x-html-safe"):
                    text_field.default_output_type = "text/html"
                    logger.info(
                        "Set default_output_type on %s %s" %(
                            obj.portal_type, obj.absolute_url(1)))
            if count % 1000 == 0:
                transaction.commit()
                logger.info('Commited after %d items' % count)
        logger.info("Possibly invalid brains: %s" % broken_brains)
        transaction.commit()
    return "Done"


# portal_types = pc.uniqueValuesFor("portal_type")
# ignore_pts = [
#     "Directive", "FormCustomScriptAdapter", "FormDateField",
#     "FormFileField", "FormReadonlyStringField", "FormSaveDataAdapter",
#     "FormTextField", "Inverse Implicator", "Ploneboard", "Ruleset",
#     "Ruleset Collection", "Type Constraint", "VdexLangstring",
#     "whoswho"]

# one_of_each_type = []

# for pt in portal_types:
#     if pt not in ignore_pts:
#         print pt
#         one_of_each_type.append(
#             pc.searchResults({"portal_type":pt})[0].getObject())

# for item in one_of_each_type:
#     print item.portal_type
#     for field in item.Schema().fields():
#         if getattr(field, "default_output_type", None):
#             output_type = field.default_output_type
#             if output_type == "text/x-html-safe":
#                 text_fields.setdefault(
#                     item.portal_type, []).append(str(field))



# {'Blog Entry': ['<Field text(text:rw)>'],
#  'CallForContractors': ['<Field text(text:rw)>', '<Field info(text:rw)>'],
#  'Document': ['<Field text(text:rw)>'],
#  'Event': ['<Field text(text:rw)>'],
#  'FormFolder': ['<Field formPrologue(text:rw)>',
#   '<Field formEpilogue(text:rw)>'],
#  'FormThanksPage': ['<Field thanksPrologue(text:rw)>',
#   '<Field thanksEpilogue(text:rw)>',
#   '<Field noSubmitMessage(text:rw)>'],
#  'HelpCenterFAQ': ['<Field text(text:rw)>'],
#  'News Item': ['<Field text(text:rw)>'],
#  'OSH_Link': ['<Field text(text:rw)>'],
#  'PressContact': ['<Field text(text:rw)>'],
#  'PressRelease': ['<Field text(text:rw)>'],
#  'PressRoom': ['<Field text(text:rw)>'],
#  'Provider': ['<Field description(text:rw)>'],
#  'PublicJobVacancy': ['<Field text(text:rw)>'],
#  'RALink': ['<Field text(text:rw)>'],
#  'RichDocument': ['<Field text(text:rw)>'],
#  'SPSeminar': ['<Field summary(text:rw)>',
#   '<Field conclusions(text:rw)>',
#   '<Field furtherActions(text:rw)>'],
#  'SPSpeaker': ['<Field biography(text:rw)>'],
#  'SPSpeech': ['<Field text(text:rw)>'],
#  'Scenario': ['<Field problem(text:rw)>',
#   '<Field solution(text:rw)>',
#   '<Field note(text:rw)>'],
#  'Topic': ['<Field text(text:rw)>']}


