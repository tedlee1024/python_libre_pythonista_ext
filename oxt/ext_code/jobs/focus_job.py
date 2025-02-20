# region imports
from __future__ import annotations
from typing import Any, cast, TYPE_CHECKING, Type
import contextlib
import uno
import unohelper
from com.sun.star.task import XJob


def _conditions_met() -> bool:
    with contextlib.suppress(Exception):
        from ___lo_pip___.install.requirements_check import RequirementsCheck

        return RequirementsCheck().run_imports_ready()
    return False


if TYPE_CHECKING:
    _CONDITIONS_MET = True
    # just for design time
    from ooodev.loader import Lo
    from ooodev.calc import CalcDoc
    from ooodev.events.args.event_args import EventArgs
    from ooodev.utils.helper.dot_dict import DotDict
    from ooodev.loader.inst.lo_loader import LoLoader
    from ...___lo_pip___.oxt_logger import OxtLogger
    from ...pythonpath.libre_pythonista_lib.event.shared_event import SharedEvent
    from ...pythonpath.libre_pythonista_lib.event.shared_cb import SharedCb
    from ...pythonpath.libre_pythonista_lib.const.event_const import (
        DOCUMENT_FOCUS_GAINED,
        DOCUMENT_FOCUS_LOST,
        CB_DOC_FOCUS_GAINED,
        CB_DOC_FOCUS_LOST,
    )
else:
    _CONDITIONS_MET = _conditions_met()
    if _CONDITIONS_MET:
        from ooodev.loader.inst.lo_loader import LoLoader
        from ooodev.loader import Lo
        from ooodev.calc import CalcDoc
        from ooodev.events.args.event_args import EventArgs
        from ooodev.utils.helper.dot_dict import DotDict
        from libre_pythonista_lib.event.shared_event import SharedEvent
        from libre_pythonista_lib.event.shared_cb import SharedCb
        from libre_pythonista_lib.const.event_const import (
            DOCUMENT_FOCUS_GAINED,
            DOCUMENT_FOCUS_LOST,
            CB_DOC_FOCUS_GAINED,
            CB_DOC_FOCUS_LOST,
        )
# endregion imports

# region Constants


# endregion Constants


# region XJob
class CalcDocFocusJob(XJob, unohelper.Base):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.CalcDocFocusJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    # region Init

    def __init__(self, ctx):
        XJob.__init__(self)
        unohelper.Base.__init__(self)
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
        self._log.debug("execute")
        try:
            # loader = Lo.load_office()
            self._log.debug(f"Args Length: {len(args)}")
            arg1 = args[0]

            for struct in arg1.Value:
                self._log.debug(f"Struct: {struct.Name}")
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")
            if self.document is None:
                self._log.debug("Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document Loading is a spreadsheet")
            else:
                self._log.debug("Document Loading not a spreadsheet")
                return
            run_id = self.document.RuntimeUID
            self._log.debug(f"Got Focus for Run ID: {run_id}")
            if not _CONDITIONS_MET:
                self._log.debug("Conditions not met. Returning.")
                return
            if Lo.current_lo:  # might not be init yet
                Lo.current_lo.current_doc = self.document
                if self._log.is_debug:
                    lo_doc = cast(CalcDoc, Lo.current_doc)
                    self._log.debug(f"Current Focus2 Lo Document Run ID: {lo_doc.runtime_uid}")
                    are_equal = lo_doc.component == self.document
                    self._log.debug(f"Are Equal: {are_equal}")
                doc = CalcDoc.get_doc_from_component(self.document)

                sc = SharedCb()
                if CB_DOC_FOCUS_GAINED in sc:
                    sc.execute(CB_DOC_FOCUS_GAINED)

                se = SharedEvent(doc)
                eargs = EventArgs(self)
                eargs.event_data = DotDict(run_id=run_id, doc=doc, event="focus", doc_type=doc.DOC_TYPE)
                se.trigger_event(DOCUMENT_FOCUS_GAINED, eargs)

        except Exception as e:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="CalcDocFocusJob")

    # endregion Logging
    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)


class CalcDocUnFocusJob(unohelper.Base, XJob):
    """Python UNO Component that implements the com.sun.star.task.Job interface."""

    IMPLE_NAME = "___lo_identifier___.CalcDocUnFocusJob"
    SERVICE_NAMES = ("com.sun.star.task.Job",)

    # region Init

    def __init__(self, ctx):
        self.ctx = ctx
        self.document = None
        self._log = self._get_local_logger()

    # endregion Init

    # region execute
    def execute(self, args: Any) -> None:
        self._log.debug("execute")
        try:
            # loader = Lo.load_office()
            self._log.debug(f"Args Length: {len(args)}")
            arg1 = args[0]

            for struct in arg1.Value:
                self._log.debug(f"Struct: {struct.Name}")
                if struct.Name == "Model":
                    self.document = struct.Value
                    self._log.debug("Document Found")
            if self.document is None:
                self._log.debug("Document is None")
                return
            if self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument"):
                self._log.debug("Document Loading is a spreadsheet")
            else:
                self._log.debug("Document Loading not a spreadsheet")
                return
            run_id = self.document.RuntimeUID
            self._log.debug(f"Lost Focus for Run ID: {run_id}")
            if not _CONDITIONS_MET:
                self._log.debug("Conditions not met. Returning.")
                return
            doc = CalcDoc.get_doc_from_component(self.document)
            if self._log.is_debug:
                try:
                    lo_doc = cast(CalcDoc, Lo.current_doc)
                    self._log.debug(f"Current Lo Document Run ID: {lo_doc.runtime_uid}")
                except Exception:
                    self._log.debug("Current Lo Document not found")

            # sc = SharedCb()
            # if CB_DOC_FOCUS_LOST in sc:
            #     sc.execute(CB_DOC_FOCUS_LOST)

            se = SharedEvent(doc)
            eargs = EventArgs(self)
            eargs.event_data = DotDict(run_id=run_id, doc=doc, event="unfocus", doc_type=doc.DOC_TYPE)
            se.trigger_event(DOCUMENT_FOCUS_LOST, eargs)

        except Exception as e:
            self._log.error("Error getting current document", exc_info=True)
            return

    # endregion execute

    # region Logging

    def _get_local_logger(self) -> OxtLogger:
        from ___lo_pip___.oxt_logger import OxtLogger  # type: ignore

        return OxtLogger(log_name="CalcDocUnFocusJob")

    # endregion Logging
    @classmethod
    def get_imple(cls):
        return (cls, cls.IMPLE_NAME, cls.SERVICE_NAMES)


# endregion XJob

# region Implementation

g_TypeTable = {}
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation(*CalcDocFocusJob.get_imple())
g_ImplementationHelper.addImplementation(*CalcDocUnFocusJob.get_imple())

# endregion Implementation
