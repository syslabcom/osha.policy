# patching the Generator class of LinguaPlone's utils

# Reason: the generatedAccessor is too trusting that the underlying
# schema really contains a field:
# return schema[name].get(self, **kw)
# The field denoted by "name" might be absent if a local SiteManager
# is responsible for extending the schema with this field. If that
# schema-extender called generateMethods, the accessor is present
# globally. But if the accessor is then called outside of the Site
# Manager's context, the field will be absent from the schema.

# Only one line is actually modified

print "\nosha.policy: patching Products.LinguaPlone.utils.Generator"

from Products.Archetypes.ClassGen import Generator as ATGenerator
from Products.Archetypes.ClassGen import GeneratorError
from Products.LinguaPlone import utils
from types import FunctionType as function

class Generator(ATGenerator):
    """Generates methods for language independent fields."""

    def makeMethod(self, klass, field, mode, methodName):
        name = field.getName()
        method = None
        if mode == "r":
            def generatedAccessor(self, **kw):
                """Default Accessor."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                return getattr(schema, name, None) and \
                    schema[name].get(self, **kw)
            method = generatedAccessor
        elif mode == "m":
            def generatedEditAccessor(self, **kw):
                """Default Edit Accessor."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                return schema[name].getRaw(self, **kw)
            method = generatedEditAccessor
        elif mode == "w":
            # the generatedMutator doesn't actually mutate, but calls a
            # translation mutator on all translations, including self.
            def generatedMutator(self, value, **kw):
                """Default Mutator."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                # translationMethodName is always present, as it is set in the generator
                translationMethodName = getattr(getattr(self, schema[name].mutator, None), '_lp_mutator', None)
                if translationMethodName is None: # Houston, we have a problem
                    return schema[name].set(self, value, **kw)
                # Instead of additional classgen magic, we check the language independent
                if not schema[name].languageIndependent:
                    return getattr(self, translationMethodName)(value, **kw)
                # Look up the actual mutator and delegate to it.
                translations = [t[0] for t in \
                                hasattr(self, 'getTranslations') and \
                                self.getTranslations().values() or []]
                # reverse to return the result of the canonical mutator
                translations.reverse()
                res = None
                for t in translations:
                    res = getattr(t, translationMethodName)(value, **kw)
                return res
            method = generatedMutator
        elif mode == "t":
            # The translation mutator that changes data
            def generatedTranslationMutator(self, value, **kw):
                """Delegated Mutator."""
                if kw.has_key('schema'):
                    schema = kw['schema']
                else:
                    schema = self.Schema()
                    kw['schema'] = schema
                return schema[name].set(self, value, **kw)
            method = generatedTranslationMutator
        else:
            raise GeneratorError("""Unhandled mode for method creation:
            %s:%s -> %s:%s""" %(klass.__name__,
                                name,
                                methodName,
                                mode))

        # Zope security requires all security protected methods to have a
        # function name. It uses this name to determine which roles are allowed
        # to access the method.
        # This code is renaming the internal name from e.g. generatedAccessor to
        # methodName.
        method = function(method.func_code,
                          method.func_globals,
                          methodName,
                          method.func_defaults,
                          method.func_closure,
                         )
        method._lp_generated = True # Note that we generated this method
        method._lp_generated_by = klass.__name__
        if mode == 'w': # The method to delegate to
            method._lp_mutator = self.computeMethodName(field, 't')
        setattr(klass, methodName, method)

utils.Generator = Generator
