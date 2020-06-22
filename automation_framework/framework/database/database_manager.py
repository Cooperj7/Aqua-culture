from collections import OrderedDict
import logging as log


from framework.database import database
from framework.io.io import Io, IoType


class DatabaseManager(Io):
    """
    Preforms managerial tasks of the data in the database
    """

    def __init__(self, name: str, actions: OrderedDict, database_name: str, max_data_age: int):

        super().__init__(name, IoType.MANGER, actions, [])
        self.database_name = database_name
        self.max_data_age = max_data_age

    def purge_old_sensor_data(self) -> None:
        """ Purges old data to keep tables from getting to large """

        log.getLogger().debug(f"STARTING purge_old_sensor_data 'Database'")

        # Rows more than 14 days should not be kept. Performance suffers greatly.
        database.purge_old_data(self.database_name, "sensors", self.max_data_age)

        log.getLogger().debug(f"DONE purge_old_sensor_data 'Database'")


