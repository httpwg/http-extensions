---
title: Opportunistic Security for HTTP
abbrev: Opportunistic HTTP Security
docname: draft-ietf-httpbis-http2-encryption-latest
date: 2017
category: exp

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft

stand_alone: yes
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline]

author:
 -
    ins: M. Nottingham
    name: Mark Nottingham
    organization:
    email: mnot@mnot.net
    uri: https://www.mnot.net/
 -
    ins: M. Thomson
    name: Martin Thomson
    organization: Mozilla
    email: martin.thomson@gmail.com

normative:
  RFC2119:
  RFC2818:
  RFC5246:
  RFC5785:
  RFC6454:
  RFC7159:
  RFC7230:
  RFC7232:
  RFC7234:
  RFC7540:
  RFC7838:

informative:
  RFC7258:
  RFC7435:
  RFC7469:
  W3C.CR-mixed-content-20160802:


--- abstract

This document describes how `http` URIs can be accessed using Transport Layer Security (TLS) to
mitigate pervasive monitoring attacks.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org),
which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source code and issues list
for this draft can be found at <https://github.com/httpwg/http-extensions/labels/opp-sec>.

--- middle

# Introduction

This document describes a use of HTTP Alternative Services {{RFC7838}} to decouple
the URI scheme from the use and configuration of underlying encryption, allowing a `http` URI
{{RFC7230}} to be accessed using Transport Layer Security (TLS) {{RFC5246}} opportunistically.

Serving `https` URIs requires avoiding Mixed Content {{W3C.CR-mixed-content-20160802}}, which is
problematic in many deployments. This document describes a usage model whereby sites can serve
`http` URIs over TLS, thereby avoiding these issues, while still providing protection against
passive attacks.

Opportunistic Security {{RFC7435}} does not provide the same guarantees as using TLS with `https`
URIs; it is vulnerable to active attacks, and does not change the security context of the
connection. Normally, users will not be able to tell that it is in use (i.e., there will be no
"lock icon").


## Goals and Non-Goals

The immediate goal is to make the use of HTTP more robust in the face of pervasive passive
monitoring {{RFC7258}}.

A secondary (but significant) goal is to provide for ease of implementation, deployment and
operation. This mechanism is expected to have a minimal impact upon performance, and require a
trivial administrative effort to configure.

Preventing active attacks (such as a Man-in-the-Middle) is a non-goal for this specification.
Furthermore, this specification is not intended to replace or offer an alternative to `https`, since
it both prevents active attacks and invokes a more stringent security model in most clients.

## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
{{RFC2119}}.


# Using HTTP URIs over TLS

An origin server that supports the resolution of `http` URIs can indicate support for this
specification by providing an alternative service advertisement {{RFC7838}} for a protocol
identifier that uses TLS, such as `h2` {{RFC7540}}.  Such a protocol MUST include an explicit
indication of the scheme of the resource.  This excludes HTTP/1.1; HTTP/1.1 clients are forbidden
from including the absolute form of a URI in requests to origin servers (see Section 5.3.1 of
{{RFC7230}}).

A client that receives such an advertisement MAY make future requests intended for the associated
origin {{RFC6454}} to the identified service (as specified by {{RFC7838}}), provided that the
alternative service opts in as described in {{opt-in}}.

A client that places the importance of protection against passive attacks over performance might
choose to withhold requests until an encrypted connection is available. However, if such a
connection cannot be successfully established, the client can resume its use of the cleartext
connection.

A client can also explicitly probe for an alternative service advertisement by sending a request
that bears little or no sensitive information, such as one with the OPTIONS method. Likewise,
clients with existing alternative services information could make such a request before they
expire, in order minimize the delays that might be incurred.

Client certificates are not meaningful for URLs with the `http` scheme, and therefore clients
creating new TLS connections to alternative services for the purposes of this specification MUST
NOT present them. A server that also provides `https` resources on the same port can request a
certificate during the TLS handshake, but it MUST NOT abort the handshake if the client does not
provide one.


## Alternative Server Opt-In {#opt-in}

It is possible that the server might become confused about whether requests' URLs have a `http` or
`https` scheme, for various reasons; see {{confuse}}. To ensure that the alternative service has
opted into serving `http` URLs over TLS, clients are required to perform additional checks before
directing `http` requests to it.

Clients MUST NOT send `http` requests over a secured connection, unless the chosen alternative
service presents a certificate that is valid for the origin as defined in {{RFC2818}} (this also
establishes "reasonable assurances" for the purposes of {RFC7838}}) and they have obtained a
valid http-opportunistic response for an origin (as per {{well-known}}).  An exception to the
last restriction is made for requests for the "http-opportunistic" well-known URI.

For example, assuming the following request is made over a TLS connection that is successfully
authenticated for those origins, the following request/response pair would allow requests for the
origins "http://www.example.com" or "http://example.com" to be sent using a secured connection:

~~~ example
HEADERS
  + END_STREAM
  + END_HEADERS
    :method = GET
    :scheme = http
    :path = /.well-known/http-opportunistic
    host: example.com

HEADERS
    :status = 200
    content-type = application/json
DATA
  + END_STREAM
[ "http://www.example.com", "http://example.com" ]
~~~

Though this document describes multiple origins, this is only for operational convenience.  Only
a request made to an origin (over an authenticated connection) can be used to acquire this
resource for that origin.  Thus in the example, the request to `http://example.com` cannot be
assumed to also provide an http-opportunistic response for `http://www.example.com`.


## Interaction with "https" URIs

Clients MUST NOT send `http` requests and `https` requests on the same connection.  Similarly,
clients MUST NOT send `http` requests for multiple origins on the same connection.


## The "http-opportunistic" well-known URI {#well-known}

This specification defines the "http-opportunistic" well-known URI {{RFC5785}}. A client is said to
have a valid http-opportunistic response for a given origin when:

* The client has requested the well-known URI from the origin over an authenticated connection
  and a 200 (OK) response was provided, and

* That response is fresh {{RFC7234}} (potentially through revalidation {{RFC7232}}), and

* That response has the media type "application/json", and

* That response's payload, when parsed as JSON {{RFC7159}}, contains an array as the root, and

* The array contains a string that is a case-insensitive character-for-character match
  for the origin in question, serialised into Unicode as per Section 6.1 of {{RFC6454}}.

A client MAY treat an "http-opportunistic" resource as invalid if the contains values that are not
strings.

This document does not define semantics for "http-opportunistic" resources on an `https` origin,
nor does it define semantics if the resource includes `https` origins.

Any strongly authenticated alternative service can provide this response.  That is, as long as
the http-opportunistic response is valid, any authenticated alternative service can be used for
that origin.

Clients that use cached http-opportunistic responses MUST ensure that their cache is cleared of
any responses that were acquired over an unauthenticated connection.  Revalidating an
unauthenticated response using an authenticated connection does not ensure the integrity of the
response.


# IANA Considerations

This specification registers a Well-Known URI {{RFC5785}}:

* URI Suffix: http-opportunistic
* Change Controller: IETF
* Specification Document(s): {{well-known}} of \[this specification\]
* Related Information:


# Security Considerations {#security}

## Security Indicators

User Agents MUST NOT provide any special security indicia when an `http` resource is acquired using
TLS. In particular, indicators that might suggest the same level of security as `https` MUST NOT be
used (e.g., a "lock device").


## Downgrade Attacks {#downgrade}

A downgrade attack against the negotiation for TLS is possible.

For example, because the `Alt-Svc` header field {{RFC7838}} likely appears in an unauthenticated
and unencrypted channel, it is subject to downgrade by network attackers. In its simplest form, an
attacker that wants the connection to remain in the clear need only strip the `Alt-Svc` header
field from responses.


## Privacy Considerations {#privacy}

Cached alternative services can be used to track clients over time; e.g., using a user-specific
hostname. Clearing the cache reduces the ability of servers to track clients; therefore clients
MUST clear cached alternative service information when clearing other origin-based state (i.e.,
cookies).


## Confusion Regarding Request Scheme {#confuse}

HTTP implementations and applications sometimes use ambient signals to determine if a request is
for an `https` resource; for example, they might look for TLS on the stack, or a server port number
of 443.

This might be due to expected limitations in the protocol (the most common HTTP/1.1 request form
does not carry an explicit indication of the URI scheme and the resource might have been developed
assuming HTTP/1.1), or it may be because how the server and application are implemented (often,
they are two separate entities, with a variety of possible interfaces between them).

Any security decisions based upon this information could be misled by the deployment of this
specification, because it violates the assumption that the use of TLS (or port 443) means that the
client is accessing a HTTPS URI, and operating in the security context implied by HTTPS.

Therefore, servers need to carefully examine the use of such signals before deploying this
specification.


## Server Controls

This specification requires that a server send both an Alternative Service advertisement and host
content in a well-known location to send HTTP requests over TLS. Servers SHOULD take suitable
measures to ensure that the content of the well-known resource remains under their control.
Likewise, because the Alt-Svc header field is used to describe policies across an entire origin,
servers SHOULD NOT permit user content to set or modify the value of this header.


--- back

# Acknowledgements

Mike Bishop contributed significant text to this document.

Thanks to Patrick McManus, Stefan Eissing, Eliot Lear, Stephen Farrell, Guy Podjarny, Stephen Ludin,
Erik Nygren, Paul Hoffman, Adam Langley, Eric Rescorla, Julian Reschke, Kari Hurtta, and Richard
Barnes for their feedback and suggestions.
