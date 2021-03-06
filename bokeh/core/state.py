''' Encapsulate implicit state that is useful for Bokeh plotting APIs.

.. note::
    While ``State`` objects can also be manipulated explicitly, they are
    automatically configured when the functions :func:`~bokeh.io.output_file`,
    etc. from :ref:`bokeh.io` are used, so this is not necessary under
    typical usage.

Generating output for Bokeh plots requires coordinating several things:

:class:`~bokeh.document.Document`
    Groups together Bokeh models that may be shared between plots (e.g.,
    range or data source objects) into one common strucure.

:class:`~bokeh.resources.Resources`
    Control how JavaScript and CSS for the client library BokehJS are
    included and used in the generated output.

It is possible to handle the configuration of these things manually, and some
examples of doing this can be found in ``examples/models`` directory. When
developing sophisticated applications, it may be necessary or desirable to work
at this level. However, for general use this would quickly become burdensome.
This module provides a ``State`` class that encapsulates these objects and
ensures their proper configuration in many common usage scenarios.

'''
from __future__ import absolute_import

import logging
logger = logging.getLogger(__name__)

import os

from ..document import Document
from ..resources import Resources, _SessionCoordinates
from ..client import DEFAULT_SESSION_ID

class State(object):
    ''' Manage state related to controlling Bokeh output.

    '''

    def __init__(self):
        self.last_comms_handle = None
        self.reset()

    @property
    def document(self):
        ''' A default :class:`~bokeh.document.Document` to use for all
        output operations.

        '''
        return self._document

    @document.setter
    def document(self, doc):
        self._document = doc

    @property
    def file(self):
        ''' A dict with the default configuration for file output (READ ONLY)

        The dictionary value has the following form:

        .. code-block:: python

            {
                'filename'  : # filename to use when saving
                'resources' : # resources configuration
                'title'     : # a title for the HTML document
            }

        '''
        return self._file

    @property
    def notebook(self):
        ''' Whether to generate notebook output on show operations. (READ ONLY)

        '''
        return self._notebook

    @property
    def server_enabled(self):
        ''' Whether to generate output on a Bokeh server. (READ ONLY)

        .. warning::
            This property is deprecated.

        '''
        return self._server_enabled

    @property
    def session_id(self):
        ''' A default session ID for Bokeh server output. (READ ONLY)

        .. warning::
            This property is deprecated.

        '''
        return self._session_coords.session_id

    @property
    def session_id_allowing_none(self):
        ''' A session ID for Bokeh server output, or ``None``. (READ ONLY)

        .. warning::
            This property is deprecated.

        '''
        return self._session_coords.session_id_allowing_none

    @property
    def url(self):
        ''' A base URL (not including any app path) for a Bokeh server.

        .. warning::
            This property is deprecated.

        '''
        return self._session_coords.url

    @property
    def server_url(self):
        ''' A full URL (including the app path) for a Bokeh server app.

        .. warning::
            This property is deprecated.

        '''
        return self._session_coords.server_url

    @property
    def app_path(self):
        ''' A relative app path for a Bokeh server app.

        .. warning::
            This property is deprecated.

        '''
        return self._session_coords.app_path

    def _reset_keeping_doc(self):
        ''' Reset output modes but DO NOT replace the default Document

        '''
        self._file = None
        self._notebook = False
        self._session_coords = _SessionCoordinates(dict())
        self._server_enabled = False

    def _reset_with_doc(self, doc):
        ''' Reset output modes but DO replace the default Document

        '''
        self._document = doc
        self._reset_keeping_doc()

    def reset(self):
        ''' Deactivate all currently active output modes and set ``curdoc()``
        to a fresh empty ``Document``.

        Subsequent calls to ``show()`` will not render until a new output mode
        is activated.

        Returns:
            None

        '''
        self._reset_with_doc(Document())

    def output_file(self, filename, title="Bokeh Plot", mode="cdn", root_dir=None):
        ''' Configure output to a standalone HTML file.

        Calling ``output_file`` not clear the effects of any other calls to
        ``output_notebook``, etc. It adds an additional output destination
        (publishing to HTML files). Any other active output modes continue
        to be active.

        Args:
            filename (str) : a filename for saving the HTML document

            title (str, optional) : a title for the HTML document

            mode (str, optional) : how to include BokehJS (default: ``'cdn'``)

                One of: ``'inline'``, ``'cdn'``, ``'relative(-dev)'`` or
                ``'absolute(-dev)'``. See :class:`~bokeh.resources.Resources`
                for more details.

            root_dir (str, optional) : root dir to use for absolute resources
                (default: None)

                This value is ignored for other resource types, e.g. ``INLINE`` or``CDN``.

        .. warning::
            The specified output file will be overwritten on every save, e.g.,
            every time ``show()`` or ``save()`` is called.

        '''
        self._file = {
            'filename'  : filename,
            'resources' : Resources(mode=mode, root_dir=root_dir),
            'title'     : title
        }

        if os.path.isfile(filename):
            logger.info("Session output file '%s' already exists, will be overwritten." % filename)

    def output_notebook(self):
        ''' Generate output in Jupyter  notebook cells.

        Calling ``output_notebook`` not clear the effects of any other calls
        to ``output_file``, etc. It adds an additional output destination
        (publishing to notebook output cells). Any other active output modes
        continue to be active.

        Returns:
            None

        '''
        self._notebook = True

    def output_server(self, session_id=DEFAULT_SESSION_ID, url="default", app_path='/'):
        ''' Store Bokeh plots and documents on a Bokeh server.

        .. warning::
            The use of the higher level function ``bokeh.io.output_server``
            has be deprecated. This support function will also be removed
            when that deprecation is complete.

        Args:
            session_id (str) : Name of session to push on Bokeh server

                ***Any existing session with the same id will be overwritten.***

            url (str, optional) : base URL of the Bokeh server (default: "default")
                If "default" use the default localhost URL.

            app_path (str, optional) : relative path of the app on the Bokeh server
                (default: "/")

        Returns:
            None

        '''
        self._session_coords = _SessionCoordinates(dict(session_id=session_id,
                                                        url=url,
                                                        app_path=app_path))

        self._server_enabled = True
