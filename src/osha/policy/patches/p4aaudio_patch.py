try:
    from p4a.ploneimage import sitesetup
    sitesetup.addSmartFolderIndexAndMetadata = lambda a:a
    sitesetup.setup_metadata = lambda a:a
    sitesetup.setup_indexes = lambda a:a
except ImportError:
    pass

