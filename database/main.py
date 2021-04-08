import logging
import sqlalchemy
from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from database.config import DB_SERVER, DB_USER, DB_PASS, DB_NAME
from sqlalchemy import Column, Integer, String
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

Base = declarative_base()


class KataDasar(Base):
    __tablename__ = 'tb_katadasar'
    id = Column(Integer, primary_key=True)
    kata = Column(String(70))
    tipe = Column(String(25))


class BaseDb(object):

    def __init__(self):
        # Initial logger
        self.logger = logging.getLogger(self.__class__.__name__)
        # Initial engine
        self.engine = create_engine('mysql://{user}:{password}@{host}:3306/{db_name}'
                                    .format(user=DB_USER, password=DB_PASS, host=DB_SERVER, db_name=DB_NAME))

        # =================================
        # Run this code to generate an automatic table
        # -> Base.metadata.create_all(self.engine)
        # =================================

    def connect(self):
        self.logger.info("Opening MySQL connection")
        # Bind engine
        Session = sessionmaker(bind=self.engine)
        # Start connection
        self.session = Session()
        # Start engine
        self.engine.connect()

    class Decorators(object):
        @classmethod
        def retry_db_errors(self, function):
            def db_func_wrapper(BaseDb, item, column=None, value=None, limit=None):
                try:
                    return function(BaseDb, item, column, value, limit)
                except (AttributeError, sqlalchemy.exc.OperationalError) as e:
                    BaseDb.logger.warning("Error message: {}".format(e.args))
                    BaseDb.connect()
                    raise e

            return db_func_wrapper

    @retry(retry=retry_if_exception_type((AttributeError, sqlalchemy.exc.OperationalError)),
           stop=stop_after_attempt(7), wait=wait_fixed(2))
    @Decorators.retry_db_errors
    def insert(self, item, column=None, value=None, limit=None):
        # Open the connection
        self.connect()

        # Catch error when insert data (Ex: Duplicate entry)
        try:
            self.session.add(item)
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            self.session.rollback()
            if "Duplicate entry" in str(e):
                self.logger.warning(
                    "Error message: Duplicate entry for key, item not inserted")
            else:
                self.logger.warning("Error message: {}".format(e.__cause__))

        # Close the connection
        self.disconnect()

    @retry(retry=retry_if_exception_type((AttributeError, sqlalchemy.exc.OperationalError)),
           stop=stop_after_attempt(7), wait=wait_fixed(2))
    @Decorators.retry_db_errors
    def insertOrUpdateBulk(self, type, column=None, value=None, limit=None):
        # Open the connection
        self.connect()

        # To split items to insert or update
        updateItems = []
        insertItems = []

        # Create dict with keys id of items
        newValues = {}
        for item in value:
            newValues[str(item.id)] = item

        # Check each id of items which already exist in the database
        for i in self.session.query(type).filter(type.id.in_(newValues.keys())).all():
            updateItems.append(vars(newValues[str(i.id)]))
            newValues.pop(str(i.id))

        for j in newValues:
            insertItems.append(vars(newValues[str(j)]))

        # Only add those posts which did not exist in the database
        self.session.bulk_update_mappings(type, updateItems)

        # Only merge those posts which already exist in the database
        self.session.bulk_insert_mappings(type, insertItems)

        # commit updates and inserts to the database
        self.session.commit()

        # Close the connection
        self.disconnect()

    @retry(retry=retry_if_exception_type((AttributeError, sqlalchemy.exc.OperationalError)),
           stop=stop_after_attempt(7), wait=wait_fixed(2))
    @Decorators.retry_db_errors
    def update(self, item, column=None, value=None, limit=None):
        # Open the connection
        self.connect()
        self.session.merge(item)
        self.session.commit()
        # Close the connection
        self.disconnect()

    @retry(retry=retry_if_exception_type((AttributeError, sqlalchemy.exc.OperationalError)),
           stop=stop_after_attempt(7), wait=wait_fixed(2))
    @Decorators.retry_db_errors
    def get(self, type, column, value, limit):
        # Open the connection
        self.connect()
        if limit is None:
            result = self.session.query(type).filter(column == value).all()
        else:
            result = self.session.query(type).filter(
                column == value).limit(limit).all()
        # Close the connection
        self.disconnect()
        return result

    @retry(retry=retry_if_exception_type((AttributeError, sqlalchemy.exc.OperationalError)),
           stop=stop_after_attempt(7), wait=wait_fixed(2))
    @Decorators.retry_db_errors
    def get_by_length(self, type, column, value, limit):
        # Open the connection
        self.connect()
        result = self.session.query(type).filter(
            or_(and_(func.length(KataDasar.kata) > value))).limit(limit).all()
        # Close the connection
        self.disconnect()
        return result

    @retry(retry=retry_if_exception_type((AttributeError, sqlalchemy.exc.OperationalError)),
           stop=stop_after_attempt(7), wait=wait_fixed(2))
    @Decorators.retry_db_errors
    def get_by_random(self, type, column, value, limit):
        # Open the connection
        self.connect()
        resultList = []
        for i in range(limit):
            result = self.session.query(type).filter(
                    or_(and_(func.length(KataDasar.kata) > value))).order_by(func.rand()).first()

            if result is None:
                break
            resultList.append(result)
        # Close the connection
        self.disconnect()
        return resultList

    @ retry(retry=retry_if_exception_type((AttributeError, sqlalchemy.exc.OperationalError)),
            stop=stop_after_attempt(7), wait=wait_fixed(2))
    @ Decorators.retry_db_errors
    def delete(self, type, column, value, limit=None):
        # Open the connection
        self.connect()
        self.session.query(type).filter(column == value).delete()
        self.session.commit()
        # Close the connection
        self.disconnect()

    def disconnect(self):
        if self.session is not None:
            self.logger.info("Closing MySQL connection")
            # Close engine and session
            self.engine.dispose()
            self.session.close()
            self.session = None


class KataDasarDb(BaseDb):
    # Use for insert only,
    # duplicate item will not update/insert
    def insert_item(self, item: Base):
        self.insert(item)

    # Use for insert or update bulk,
    # duplicate item will update
    # items = can different tpye
    def insert_bulk_item(self, items: 'list of Base'):
        # Get item type
        insp = type(items[0])

        # Insert or update bulk
        self.insertOrUpdateBulk(item=insp, value=items)

    # Use for insert or update,
    # duplicate item will update

    def inser_or_update_item(self, item: Base):
        self.update(item)

    # Use for get item by id
    def get_item_by_column(self, value, column):
        result = self.get(KataDasar, column=column, value=value)

        if len(result) == 0:
            return None
        else:
            return result

    def get_words_by_length(self, length, max):
        result = self.get_by_length(KataDasar, value=length, limit=max)

        if len(result) == 0:
            return None
        else:
            return result

    def get_random_words_by_length(self, length, max):
        result = self.get_by_random(KataDasar, value=length, limit=max)

        if len(result) == 0:
            return None
        else:
            return result

    # Use for delete item by id
    def delete_item_by_id(self, id: int, type: Base):
        self.delete(type, type.id)
