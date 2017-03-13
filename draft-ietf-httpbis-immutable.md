---
title: HTTP Immutable Responses
docname: draft-ietf-httpbis-immutable-latest
date: 2017
category: std
ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP

author:
 - 
  ins: P. McManus
  name: Patrick McManus
  organization: Mozilla
  email: pmcmanus@mozilla.com

normative:
 RFC7231:
 RFC7232:
 RFC7234:

informative:
  REQPERPAGE:
   target: http://httparchive.org/interesting.php#reqTotal
   title: "HTTP Archive"

--- abstract

The immutable HTTP response Cache-Control extension allows servers to
identify resources that will not be updated during their freshness
lifetime. This assures that a client never needs to revalidate a
cached fresh resource to be certain it has not been modified.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org),
which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source code and issues list
for this draft can be found at <https://github.com/httpwg/http-extensions/labels/immutable>.

--- middle

# Introduction

The HTTP freshness lifetime [RFC7234] caching attribute
specifies that a client may safely reuse a response to satisfy future
requests over a specific period of time. It does not specify that the
resource will be not be modified during that period.

For instance, a front page newspaper photo with a freshness lifetime
of one hour would mean that no user should see a photo more than one
hour old. However, the photo could be updated at any time resulting in
different users seeing different photos depending on the contents of
their caches for up to one hour. This is compliant with the caching
mechanism defined in [RFC7234].

Users that need to confirm there have been no updates to their current
cached resources typically invoke the reload (or refresh) mechanism in
the user agent. This in turn generates a conditional request [RFC7232]
and either a new representation or, if unmodified, a 304 response
[RFC7231] is returned. A user agent that manages HTML and its
dependent sub-resources may issue hundreds of conditional requests to
refresh all portions of a common HTML page [REQPERPAGE].

Through the use of the versioned URL design pattern some content
providers never create more than one variant of a sub-resource. When
these resources need an update they are simply published under a new URL,
typically embedding a variant identifier in the path, and references
to the sub-resource are updated with the new path information.

For example, https://www.example.com/101016/main.css might be updated
and republished as https://www.example.com/102026/main.css and the html that
references it is changed at the same time. This design pattern allows
a very large freshness lifetime to be applied to the sub-resource
without guessing when it will be updated in the future.

Unfortunately, the user-agent is not aware of the versioned URL design
pattern. User driven refresh events still translate into wasted
conditional requests for each sub-resource as each will return 304
responses.

The immutable HTTP response Cache-Control extension allows servers to
identify resources that will not be updated during their freshness
lifetime. This effectively instructs the client that any conditional
request for a previously served variant of that resource may be safely
skipped without worrying that it has been updated.

# The immutable Cache-Control extension

When present in an HTTP response, the immutable Cache-Control
extension indicates that the origin server will not update the representation
of that resource during the freshness lifetime of the
response.

Clients SHOULD NOT issue a conditional request during the
response's freshness lifetime (e.g. upon a reload) unless explicitly
overridden by the user (e.g. a force reload).

The immutable extension only applies during the freshness lifetime of
the response. Stale responses SHOULD be revalidated as they normally
would be in the absence of immutable.

The immutable extension takes no arguments and if any arguments are
present they have no meaning. Multiple instances of the immutable
extension are equivalent to one instance. The presence of an immutable
Cache-Control extension in a request has no effect.

## About Intermediaries

An immutable response has the same semantic meaning for proxy clients
as it does for User-Agent based clients and they therefore MAY also
presume a conditional revalidation for a response marked immutable
would return 304. A proxy client who uses immutable to anticipate a
304 response may choose whether to reply with a 304 or 200 to its
requesting client.

## Example

~~~ example
Cache-Control: max-age=31536000, immutable
~~~

# Security Considerations

The immutable mechanism acts as form of soft pinning and, as with all
pinning mechanisms, creates a vector for amplification of cache
corruption incidents. These incidents include cache poisoning
attacks. Three mechanisms are suggested for mitigation of this risk:

* Clients should ignore immutable for resources that are not
 part of an authenticated context such as HTTPS. Authenticated resources are less
 vulnerable to cache poisoning.
 
* User-Agents often provide two different refresh mechanismss: reload
  and some form of force-reload. The latter is used to rectify
  interrupted loads and other corruption. These reloads, typically
  indicated through no-cache request attributes, should ignore
  immutable as well.

* Clients should ignore immutable for resources that do not provide a
 strong indication that the stored response size is the correct
 response size such as responses delimited by connection close.

# IANA Considerations

[RFC7234] sections 7.1 and 7.1.2 require registration of the
immutable extension in the "Hypertext Transfer Protocol (HTTP) Cache
Directive Registry" with IETF Review.

* Cache-Directive: immutable
* Pointer to specification text: \[this document\]

# Acknowledgments

Thank you to Ben Maurer for partnership in developing and testing this
idea. Thank you to Amos Jeffries for help with proxy interactions.
