from slc.publications.adapter.events import ChapterUpdater, TranslationChapterUpdater

class OshaChapterUpdater(ChapterUpdater):
    """
    The Standard Chapter Updater does a workflow setting that we don't
    want. Our Chapter Links don't have a workflow at all
    """
    def setState(self, chapter, language):
        pass

class OshaTranslationChapterUpdater(TranslationChapterUpdater):
    """
    The Standard Chapter Updater does a workflow setting that we don't
    want. Our Chapter Links don't have a workflow at all
    """
    def setState(self, chapter, language):
        pass
