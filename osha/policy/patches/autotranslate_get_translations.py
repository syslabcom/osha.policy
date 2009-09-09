from slc.autotranslate import utils

def get_translations(folder, file_obj, base_filename, file_ext):
    """ 
    Return any files in folder that are deemed translations, for conforming
    to the file naming convention.
    """
    translations = {}

    # Get all the translated parent folders, and see if there are 
    # translations conforming to base_filename in them
    translated_folders = folder.getTranslations()
    for langcode in translated_folders.keys():
        if langcode == folder.getLanguage():
            continue

        parent = translated_folders[langcode][0]
        # In OSHA, the factsheets are merely the factsheet number without
        # leading zero. So en_03.pdf is only '3', which is the base_filename
        # stripped of the leading zero.
        name = base_filename.lstrip('0')
        if hasattr(parent, name):
            obj = getattr(parent, name)
            translations[langcode] = obj

    return translations

utils.get_translations = get_translations

