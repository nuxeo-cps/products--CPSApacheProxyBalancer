##############################################################################
#
# Copyright (c) 2005-2008 Nuxeo and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
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

LOG_KEY = 'CPSApacheProxyBalancer.affinity'
logger = logging.getLogger(LOG_KEY)

COOKIE_ID = 'BALANCEID'

class AffinityTool(UniqueObject, Folder):
    """.
    """
    implements(ICpsAffinityTool)
    meta_type = 'CPS Apache Proxy Balancer'

    manage_options = (Folder.manage_options)

    _properties = (
        {'id': 'cookie_domain',
         'type': 'string',
         'mode': 'w',
         'label': "Cookie domain (Optional)",
        },
    )

    cookie_domain = ''
    hostname = socket.gethostname()

    security = ClassSecurityInfo()

    def __call__(self, container, request):
        """Here is the method .
        """
        log_key = LOG_KEY + '.__call__'
        logger = logging.getLogger(log_key)
        logger.debug("...")

        # Using the post traverse hook
        request.post_traverse(*[self.mmethod, (container, request)])


    def mmethod(self, container, request):
        log_key = LOG_KEY + '.mmethod'
        logger = logging.getLogger(log_key)
        logger.debug("...")
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            logger.debug("User is anonymous, quitting")
            return
        username = mtool.getAuthenticatedMember().getUserName();
        logger.debug("username = %s" % username)
        self.setStickySession(request, username);

    security.declarePublic('setStickySessionCookie')
    def setStickySession(self, REQUEST, username):
        """.
        """
        log_key = LOG_KEY + '.setStickySession'
        logger = logging.getLogger(log_key)
        logger.debug("...")

        existing = REQUEST.cookies.get(COOKIE_ID)

        toset = self._computeStickySession(username)
        if existing != toset:
            # using relatively short lived cookies has the benefit
            # of having apache randomly retry dead workers after expiration
            exp = (DateTime() + 0.1).rfc822()
            REQUEST.RESPONSE.setCookie(COOKIE_ID, toset, path='/',
                                       expires=exp)

    def expireStickySession(self, REQUEST):
        """.
        """
        log_key = LOG_KEY + '.expireStickySession'
        logger = logging.getLogger(log_key)
        logger.debug("...")

        REQUEST.RESPONSE.expireCookie(COOKIE_ID, path='/')

    def _computeStickySession(self, username):
        """.
        """
        log_key = LOG_KEY + '._computeStickySession'
        logger = logging.getLogger(log_key)
        logger.debug("...")

        return '.'.join((username, self.hostname,
                         os.path.split(INSTANCE_HOME)[-1]))


InitializeClass(AffinityTool)


def registerHook(ob, event):
    logger.debug("...")
    tool_id = event.newName
    handle = ob.meta_type + '/' + tool_id
    container = aq_inner(aq_parent(ob))
    nc = BeforeTraverse.NameCaller(tool_id)
    logger.debug("handle = %s, container = %s, nc = %s" % (handle, container, nc))
    BeforeTraverse.registerBeforeTraverse(container, nc, handle, priority=10)
    logger.debug("Registered BeforeTraverse hook")

def unregisterHook(ob, event):
    logger.debug("...")
    tool_id = event.oldName
    handle = ob.meta_type + '/' + tool_id
    container = aq_inner(aq_parent(ob))
    logger.debug("handle = %s, container = %s" % (handle, container))
    BeforeTraverse.unregisterBeforeTraverse(container, handle)
    logger.debug("Unregistered BeforeTraverse hook")


def manage_addTool(self, id, auth_type, REQUEST=None):
    """
    """
    ob = AffinityTool()
    ob.id = id
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)



