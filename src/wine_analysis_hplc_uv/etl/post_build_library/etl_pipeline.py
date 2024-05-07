import abc
import duckdb as db
import logging

logger = logging.getLogger(__name__)


class ETLTransformerABC(abc.ABC):
    """
    ETL Transformer ABC
    """

    @abc.abstractmethod
    def __init__(
        self,
        input_tblname: str,
        output_tblname: str,
        write_to_db: bool = False,
        overwrite: bool = False,
    ):
        self.input_tblname = input_tblname
        self.output_tblname = output_tblname

        self._write_to_db: bool = False
        self._overwrite: bool = False

    @abc.abstractmethod
    def run(self, con: db.DuckDBPyConnection):
        self.con = con
        pass

    @abc.abstractmethod
    def cleanup(self):
        pass

    @property
    @abc.abstractmethod
    def write_to_db(self):
        return self._write_to_db

    @write_to_db.setter
    @abc.abstractmethod
    def write_to_db(self, val: bool):
        self._write_to_db = val

    @write_to_db.getter
    @abc.abstractmethod
    def write_to_db(self):
        return self._write_to_db

    @property
    @abc.abstractmethod
    def overwrite(self):
        return self._overwrite

    @overwrite.setter
    @abc.abstractmethod
    def overwrite(self, val: bool):
        self._overwrite = val

    @overwrite.getter
    @abc.abstractmethod
    def overwrite(self):
        return self._overwrite


class PipelineETL:
    def __init__(
        self,
        con: db.DuckDBPyConnection,
        transformers: dict[str, ETLTransformerABC],
        write_to_db: bool = False,
        overwrite: bool = False,
    ):
        """
        ETL pipeline orchastraction class.

        :param overwrite: activate 'overwrite' flag on transformers to overwrite any written objects such as tables. Defaults to False.
        :type overwrite: bool
        """

        self.con = con
        self.transformers = transformers
        self.write_to_db = write_to_db
        self.overwrite = overwrite

    def execute_pipeline(self) -> list[str]:
        """
        execute the transformers in the order they appeared in self.transformers
        """
        tformer_idx_order = {
            idx: tformer for idx, tformer in enumerate(self.transformers)
        }
        logger.info(f"Beginning pipeline execution with {tformer_idx_order}")
        self.executed_tformers: list = []

        for idx, (name, tformer) in enumerate(self.transformers.items()):
            try:
                tformer.write_to_db = self.write_to_db
                logger.debug(f"executing {idx}., {name}")
                self.executed_tformers.append(name)
                tformer.overwrite = self.overwrite
                tformer.run(con=self.con)

            except Exception as e:
                self._invert_pipeline()
                raise e

        logger.info(
            f"successully executed: {[f'{idx}. {name}' for idx, name in enumerate(self.executed_tformers)]}"
        )

        return [
            self.transformers[tformer].output_tblname
            for tformer in self.executed_tformers
        ]

    def _invert_pipeline(self) -> None:
        """
        run the cleanup methods for each component transformer, reversing any changes made
        by 'execute_pipeline'
        TODO: define this
        """
        try:
            for idx, tform_name in enumerate(reversed(self.executed_tformers)):
                self.transformers[tform_name].cleanup()
        except Exception as e:
            raise e
