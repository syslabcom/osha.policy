from collective.lead import Database
from App.config import getConfiguration


class OSHADatabase(Database):

    @property
    def _url(self):
        """Return db connection string which we read from the environment."""
        configuration = getConfiguration()
        try:
            conf = configuration.product_config['osha.policy']
            url = conf['osha.database']
        except (AttributeError, KeyError):
            raise KeyError(
                'No product config found! Cannot read osha.database '
                'connection string.'
            )
        return url

    def _setup_tables(self, metadata, tables):
        """XXX: We need to implement this method, because
        collective.lead expects it, but we don't realy need it, since
        we're working directly with the database.  """
        pass

    def _setup_mappers(self, tables, mappers):
        pass
