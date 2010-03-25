import simplejson as json
def run(self):
    lang_messages = {
        'en': {
            'required': "This field is required.",
            'email': "Please enter a valid email address.",
        },
        'nl': {
            'required': "Deze veld is verpligtend.",
            'email': "Verskaf asjeblief een geldige epos adres.",
        }
    }
    lang = self.portal_languages.getPreferredLanguage()
    messages = {}
    messages['organisation'] 	= lang_messages.get(lang, lang_messages.get('en'))
    messages['address'] 	= lang_messages.get(lang, lang_messages.get('en'))
    messages['postal_code'] 	= lang_messages.get(lang, lang_messages.get('en'))
    messages['city'] 		= lang_messages.get(lang, lang_messages.get('en'))
    messages['country'] 	= lang_messages.get(lang, lang_messages.get('en'))
    messages['firstname'] 	= lang_messages.get(lang, lang_messages.get('en'))
    messages['lastname'] 	= lang_messages.get(lang, lang_messages.get('en'))
    messages['sector'] 		= lang_messages.get(lang, lang_messages.get('en'))
    messages['email'] 		= lang_messages.get(lang, lang_messages.get('en'))
    messages['telephone'] 	= lang_messages.get(lang, lang_messages.get('en'))
    data = {'messages': messages}
    return json.dumps(data)
