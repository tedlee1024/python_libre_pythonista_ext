from __future__ import annotations
from typing import Any, cast, Tuple
from urllib.parse import parse_qs
import contextlib
import uno
import unohelper
from com.sun.star.frame import XDispatchProviderInterceptor
from com.sun.star.frame import XDispatchProvider
from com.sun.star.frame import XDispatch
from com.sun.star.util import URL
from com.sun.star.frame import DispatchDescriptor

from ooodev.loader import Lo
from ooodev.calc import CalcDoc
from ooodev.events.lo_events import LoEvents
from ooodev.events.args.event_args import EventArgs

# from ooodev.calc import CalcDoc
from ..const import (
    UNO_DISPATCH_CODE_EDIT,
    UNO_DISPATCH_CODE_EDIT_MB,
    UNO_DISPATCH_DF_STATE,
    UNO_DISPATCH_DS_STATE,
    UNO_DISPATCH_DATA_TBL_STATE,
    UNO_DISPATCH_CODE_DEL,
    UNO_DISPATCH_PY_OBJ_STATE,
    UNO_DISPATCH_CELL_SELECT,
    UNO_DISPATCH_CELL_SELECT_RECALC,
    UNO_DISPATCH_DF_CARD,
    UNO_DISPATCH_DATA_TBL_CARD,
    UNO_DISPATCH_SEL_RNG,
    UNO_DISPATCH_ABOUT,
    UNO_DISPATCH_LOG_WIN,
    UNO_DISPATCH_CELL_CTl_UPDATE,
)
from ..const.event_const import GBL_DOC_CLOSING

from .dispatch_about import DispatchAbout
from .dispatch_edit_py_cell import DispatchEditPyCell
from .dispatch_toggle_df_state import DispatchToggleDfState
from .dispatch_toggle_data_tbl_state import DispatchToggleDataTblState
from .dispatch_toggle_series_state import DispatchToggleSeriesState
from .dispatch_del_py_cell import DispatchDelPyCell
from .dispatch_py_obj_state import DispatchPyObjState
from .dispatch_cell_select import DispatchCellSelect
from .dispatch_card_df import DispatchCardDf
from .dispatch_card_tbl_data import DispatchCardTblData
from .dispatch_rng_select_popup import DispatchRngSelectPopup
from .dispatch_edit_py_cell_mb import DispatchEditPyCellMb
from .dispatch_log_window import DispatchLogWindow
from .dispatch_cell_select_recalc import DispatchCellSelectRecalc
from .dispatch_ctl_update import DispatchCtlUpdate

# from .listen.edit_status_listener import EditStatusListener
from ..log.log_inst import LogInst


class DispatchProviderInterceptor(unohelper.Base, XDispatchProviderInterceptor):
    """
    Dispatch Provider Interceptor.

    This class needs to be kept alive as long as the dispatch provider is in use.
    For this reason this class is a singleton.

    Calling the ``dispose()`` method will release the singleton instance.
    """

    _instances = {}

    def __new__(cls, doc: CalcDoc, *args, **kwargs):
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        # sc = Lo.xscript_context
        # doc = sc.getDocument()
        # uid = doc.RuntimeUID

        uid = doc.runtime_uid
        key = f"dpi_{uid}"
        if not key in cls._instances:
            inst = super(DispatchProviderInterceptor, cls).__new__(cls, *args, **kwargs)
            inst._initialized = False
            inst._key = key
            cls._instances[key] = inst
        return cls._instances[key]

    def __init__(self, doc: CalcDoc):
        if getattr(self, "_initialized", False):
            return
        self._master = cast(XDispatchProvider, None)
        self._slave = cast(XDispatchProvider, None)
        self._initialized = True
        self._key: str

    # def _convert_query_to_dict(self, query: str):
    #     return parse_qs(query)

    def _convert_query_to_dict(self, query: str):
        query_dict = parse_qs(query)
        return {k: v[0] for k, v in query_dict.items()}

    def getMasterDispatchProvider(self) -> XDispatchProvider:
        """
        access to the master XDispatchProvider of this interceptor
        """
        return self._master

    def getSlaveDispatchProvider(self) -> XDispatchProvider:
        """
        access to the slave XDispatchProvider of this interceptor
        """
        return self._slave

    def setMasterDispatchProvider(self, new_supplier: XDispatchProvider) -> None:
        """
        sets the master XDispatchProvider, which may forward calls to its XDispatchProvider.queryDispatch() to this dispatch provider.
        """
        self._master = new_supplier

    def setSlaveDispatchProvider(self, new_dispatch_provider: XDispatchProvider) -> None:
        """
        sets the slave XDispatchProvider to which calls to XDispatchProvider.queryDispatch() can be forwarded under control of this dispatch provider.
        """
        self._slave = new_dispatch_provider

    def queryDispatch(self, url: URL, target_frame_name: str, search_flags: int) -> XDispatch | None:
        """
        Searches for an XDispatch for the specified URL within the specified target frame.
        """
        if url.Protocol == "slot:":
            # not really sure if this is necessary but there have been reports in the past
            # of crashes without this check.
            return None

        log = LogInst()
        # this next line adds over 1000 lines to the log file
        # log.debug(f"DispatchProviderInterceptor.queryDispatch: {url.Complete}")

        # example log entries
        # 2024-06-19 21:23:54,872 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:Quit
        # 2024-06-19 21:23:54,872 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:About
        # 2024-06-19 21:23:54,873 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:PrinterSetup
        # 2024-06-19 21:23:54,873 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:SafeMode
        # 2024-06-19 21:23:54,874 - libre_pythonista - DEBUG - DispatchProviderInterceptor.queryDispatch: .uno:DevelopmentToolsDockingWindow

        if url.Main == UNO_DISPATCH_CODE_EDIT:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchEditPyCell")
                result = DispatchEditPyCell(sheet=args["sheet"], cell=args["cell"])
                return result
        elif url.Main == UNO_DISPATCH_CODE_EDIT_MB:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchEditPyCellMb")
                in_thread = args.get("in_thread", "0") == "1"
                result = DispatchEditPyCellMb(sheet=args["sheet"], cell=args["cell"], in_thread=in_thread)
                return result
        elif url.Main == UNO_DISPATCH_LOG_WIN:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchLogWindow")
                in_thread = args.get("in_thread", "0") == "1"
                result = DispatchLogWindow(in_thread=in_thread)
                return result
        elif url.Main == UNO_DISPATCH_DF_STATE:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchToggleDfState")
                return DispatchToggleDfState(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_DS_STATE:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchToggleSeriesState")
                return DispatchToggleSeriesState(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_DATA_TBL_STATE:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchToggleDataTblState")
                return DispatchToggleDataTblState(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_CODE_DEL:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchDelPyCell")
                return DispatchDelPyCell(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_PY_OBJ_STATE:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchPyObjState")
                return DispatchPyObjState(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_CELL_SELECT:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCellSelect")
                return DispatchCellSelect(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_CELL_SELECT_RECALC:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCellSelectRecalc")
                return DispatchCellSelectRecalc(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_DF_CARD:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCardDf")
                return DispatchCardDf(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_DATA_TBL_CARD:
            with contextlib.suppress(Exception):
                args = self._convert_query_to_dict(url.Arguments)
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCardTblData")
                return DispatchCardTblData(sheet=args["sheet"], cell=args["cell"])
        elif url.Main == UNO_DISPATCH_SEL_RNG:
            with contextlib.suppress(Exception):
                if url.Arguments:
                    args = self._convert_query_to_dict(url.Arguments)
                else:
                    args = {}
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchRngSelectPopup")
                return DispatchRngSelectPopup(**args)
        elif url.Main == UNO_DISPATCH_ABOUT:
            with contextlib.suppress(Exception):
                with log.indent(True):
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchAbout")
                return DispatchAbout()
        elif url.Main == UNO_DISPATCH_CELL_CTl_UPDATE:
            with contextlib.suppress(Exception):
                with log.indent(True):
                    args = self._convert_query_to_dict(url.Arguments)
                    log.debug(f"DispatchProviderInterceptor.queryDispatch: returning DispatchCtlUpdate")
                return DispatchCtlUpdate(sheet=args["sheet"], cell=args["cell"])

        return self._slave.queryDispatch(url, target_frame_name, search_flags)

    def queryDispatches(self, requests: Tuple[DispatchDescriptor, ...]) -> Tuple[XDispatch, ...]:
        """
        Actually this method is redundant to XDispatchProvider.queryDispatch() to avoid multiple remote calls.

        It's not allowed to pack it - because every request must match to its real result. Means: don't delete NULL entries inside this list.
        """
        return ()

    def dispose(self) -> None:
        if self._key in DispatchProviderInterceptor._instances:
            del DispatchProviderInterceptor._instances[self._key]

    @classmethod
    def has_instance(cls, doc: CalcDoc) -> bool:
        # doc = Lo.current_doc
        # doc = CalcDoc.from_current_doc()
        doc.runtime_uid
        key = f"dpi_{doc.runtime_uid}"
        return key in cls._instances


def _on_doc_closing(src: Any, event: EventArgs) -> None:
    # clean up singleton
    uid = str(event.event_data.uid)
    key = f"dpi_{uid}"
    if key in DispatchProviderInterceptor._instances:
        del DispatchProviderInterceptor._instances[key]


LoEvents().on(GBL_DOC_CLOSING, _on_doc_closing)
