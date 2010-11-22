# (C) Copyright 2008 Nuxeo SAS <http://nuxeo.com>
# Authors:
# G. Racinet <gracinet@nuxeo.com>
# M.-A. Darche <madarche@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
"""
$Id$
"""
import logging
import socket
import os

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Globals import InitializeClass, HTMLFile
from OFS.Folder import Folder
from OFS.Cache import Cacheable
from DateTime import DateTime
from ZPublisher import BeforeTraverse

from zope.interface import implements

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Sessions.BrowserIdManager import getNewBrowserId
from Products.CMFCore.utils import getToolByName, UniqueObject

from interfaces import ICpsAffinityTool

logger = logging.getLogger(__name__)

# The ID of the cookie that is used by Apache Module mod_proxy_balancer
COOKIE_ID = 'BALANCEID'

class AffinityTool(UniqueObject, Folder):
    """.
    """
    implements(ICpsAffinityTool)
    meta_type = 'CPS Apache Proxy Balancer'

    hostname = socket.gethostname()

    security = ClassSecurityInfo()

    def __call__(self, container, request):
        """.
        """
        # This method is called by the before traverse hook to register in turn
        # a post traverse hook.

        logger.debug('__call__')

        # Using the post traverse hook
        request.post_traverse(*[self.registerCallBack, (container, request)])

    def registerCallBack(self, container, request):
        # This method is called by post traverse hook
        logger = logging.getLogger(log_key)
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            logger.debug("registerCallback: User is anonymous, quitting")
            return
        username = mtool.getAuthenticatedMember().getUserName();
        logger.debug("username = %s" % username)
        self.setStickySession(request, username);

    security.declarePublic('setStickySessionCookie')
    def setStickySession(self, REQUEST, username):
        """.
        """
        existing = REQUEST.cookies.get(COOKIE_ID)
        toset = self._computeStickySession(username)
        logger.debug("setStickySession existing=%r toset=%r", existing, toset)

        if existing != toset:
            # Using relatively short lived cookies has the benefit
            # of having Apache randomly retry dead workers after expiration.
            exp = (DateTime() + 0.1).rfc822()
            REQUEST.RESPONSE.setCookie(COOKIE_ID, toset, path='/',
                                       expires=exp)

    def expireStickySession(self, REQUEST):
        """.
        """
        logger.debug("expireStickySession")
        REQUEST.RESPONSE.expireCookie(COOKIE_ID, path='/')

    def _computeStickySession(self, username):
        """.
        """
        logger.debug("_computeStickySession INSTANCE_HOME = %s", INSTANCE_HOME)

        # For example if INSTANCE_HOME is "/home/zope/zc0",
        # then os.path.split(INSTANCE_HOME)[-1] would be "zc0".
        return '.'.join((username, self.hostname,
                         os.path.split(INSTANCE_HOME)[-1]))


InitializeClass(AffinityTool)


def registerHook(ob, event):
    tool_id = event.newName
    handle = ob.meta_type + '/' + tool_id
    container = aq_inner(aq_parent(ob))
    nc = BeforeTraverse.NameCaller(tool_id)
    logger.debug("handle=%r, container=%r, nc=%r", handle, container, nc)
    BeforeTraverse.registerBeforeTraverse(container, nc, handle)
    logger.debug("Registered BeforeTraverse hook")

def unregisterHook(ob, event):
    tool_id = event.oldName
    handle = ob.meta_type + '/' + tool_id
    container = aq_inner(aq_parent(ob))
    logger.debug("handle=%r, container=%r", handle, container)
    BeforeTraverse.unregisterBeforeTraverse(container, handle)
    logger.debug("Unregistered BeforeTraverse hook")


def manage_addTool(self, id, auth_type, REQUEST=None):
    """.
    """
    ob = AffinityTool()
    ob.id = id
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
