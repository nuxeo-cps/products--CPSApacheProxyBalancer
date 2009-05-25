=======
README
=======

:Author: M.-A. Darche
:Revision: $Id$


This product `CPSApacheProxyBalancer` is about providing Zope instance affinity
for web clients on a distributed Zope environment.

The Apache Module `mod_proxy_balancer`, documented at the following address
http://httpd.apache.org/docs/2.2/mod/mod_proxy_balancer.html , is the solution
in front of the Zope cluster to redirect to one or the other Zope instance of
the ZEO cluster.

Apache Module `mod_proxy_balancer` provides similar functionalities to those of
the `Pound` load balancer program. But we prefer to use `mod_proxy_balancer`
because it is integrated in Apache and we need to use Apache anyway.

Zope instance affinity is needed when one wants authenticated users to stay on
only one Zope instance of a ZEO cluster. And of course we want non-authenticated
users (ie anonymous users) to be shuffled from one instance to the other so that
the server load is balanced.

One could want authenticated users to stay on only one Zope instance of a ZEO
cluster if the information of the user connected is not stored in the database
(which is the preferred practice to minimize writes to the ZODB
database). In CPS by default authenticated users are kept in a RAM cache in the
Zope instance. And RAM cache is not ZEO-aware by definition because it's only in
RAM and nothing is written in the ZODB.


.. Local Variables:
.. mode: rst
.. End:
.. vim: set filetype=rst:
