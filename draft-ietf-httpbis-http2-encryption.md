---
title: Opportunistic Security for HTTP
abbrev: Opportunistic HTTP Security
docname: draft-ietf-httpbis-http2-encryption-latest
date: 2016
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
    uri: http://www.mnot.net/
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
  RFC7234:
  RFC7540:
  I-D.ietf-httpbis-alt-svc:

informative:
  RFC7258:
  RFC7435:


--- abstract

This document describes how `http` URIs can be accessed using Transport Layer Security (TLS) to
mitigate pervasive monitoring attacks.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list 
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source 
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/opp-sec>.

--- middle

# Introduction

This document describes a use of HTTP Alternative Services {{I-D.ietf-httpbis-alt-svc}} to decouple
the URI scheme from the use and configuration of underlying encryption, allowing a `http` URI
{{RFC7230}} to be accessed using TLS {{RFC5246}} opportunistically.

Serving `https` URIs require acquiring and configuring a valid certificate, which means that some
deployments find supporting TLS difficult. This document describes a usage model whereby sites can
serve `http` URIs over TLS without being required to support strong server authentication.

Opportunistic Security {{RFC7435}} does not provide the same guarantees
as using TLS with `https` URIs; it is vulnerable to active attacks, and does not change the security
context of the connection. Normally, users will not be able to tell that it is in use (i.e., there
will be no "lock icon").

By its nature, this technique is vulnerable to active attacks. A mechanism for partially mitigating
them is described in {{http-tls}}.


## Goals and Non-Goals

The immediate goal is to make the use of HTTP more robust in the face of pervasive passive
monitoring {{RFC7258}}.

A secondary goal is to limit the potential for active attacks. It is not intended to offer the same
level of protection as afforded to `https` URIs, but instead to increase the likelihood that an
active attack can be detected.

A final (but significant) goal is to provide for ease of implementation, deployment and operation.
This mechanism is expected to have a minimal impact upon performance, and require a trivial
administrative effort to configure.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
{{RFC2119}}.


# Using HTTP URIs over TLS

An origin server that supports the resolution of `http` URIs can indicate support for this
specification by providing an alternative service advertisement {{I-D.ietf-httpbis-alt-svc}} for a
protocol identifier that uses TLS, such as `h2` {{RFC7540}}.

A client that receives such an advertisement MAY make future requests intended for the associated
origin ({{RFC6454}}) to the identified service (as specified by {{I-D.ietf-httpbis-alt-svc}}).

A client that places the importance of protection against passive attacks over performance might
choose to withhold requests until an encrypted connection is available. However, if such a
connection cannot be successfully established, the client can resume its use of the cleartext
connection.

A client can also explicitly probe for an alternative service advertisement by sending a request
that bears little or no sensitive information, such as one with the OPTIONS method. Likewise,
clients with existing alternative services information could make such a request before they
expire, in order minimize the delays that might be incurred.

# Server Authentication {#auth}

{{I-D.ietf-httpbis-alt-svc}} requires that an alternative service only be used when there are "reasonable assurances" that it is under control of and valid for the whole origin.

For the purposes of this specification, there are two ways to achieve this:

1. Using TLS with a certificate that validates as per {{RFC2818}}, or
2. Confirming that both the origin and the alternative service support this specification by interacting with the "http-opportunistic" well-known URI (see {{well-known}}).

The latter approach allows deployment without the use of valid certificates, to encourage
deployment of opportunistic security. When it is in use, the alternative service can provide
any certificate, or even select TLS cipher suites that do not include authentication.



## The "http-opportunistic" well-known URI {#well-known}

To establish reasonable assurances that an origin allows an alternative service on the same host as
it when the alternative does not have a valid certificate (as per {{auth}}), an client can fetch
the "http-opportunistic" well-known URI {{RFC5785}} from the origin.

A client MAY consider there to be reasonable assurances when:

* It has obtained a 200 (OK) response for the well-known URI from the origin, or refreshed one in cache {{RFC7234}}, and

* That response has the media type "application/json", and

* That response's payload, when parsed as JSON {{RFC7159}}, contains a root object with a member "origins" whose value is a list of strings, one of which is a case-insensitive character-for-character match for the origin in question, serialised into Unicode as per {{RFC6454}}, Section 6.1, and

* The origin and alternative service's hostnames are the same when compared in a case-insensitive fashion, and

* The chosen alternative service returns the same response as above.

For example, this request/response pair would constitute reasonable assurances for the origin "http://www.example.com:80" for any alternative service also on "www.example.com":

~~~
GET /.well-known/http-opportunistic HTTP/1.1
Host: www.example.com

HTTP/1.1 200 OK
Content-Type: application/json
Connection: close

{
  "origins": ["http://example.com:80", "http://www.example.com/:81"]
}
~~~


# Interaction with "https" URIs

When using alternative services, requests for resources identified by both `http` and `https` URIs
might use the same connection, because HTTP/2 permits requests for multiple origins on the same
connection.

Since `https` URIs rely on server authentication, a connection that is initially created for `http`
URIs without authenticating the server cannot be used for `https` URIs until the server certificate
is successfully authenticated. Section 3.1 of {{RFC2818}} describes the basic mechanism, though the
authentication considerations in {{I-D.ietf-httpbis-alt-svc}} also apply.

Connections that are established without any means of server authentication (for instance, the
purely anonymous TLS cipher suites), cannot be used for `https` URIs.


# Requiring Use of TLS {#http-tls}

Editors' Note: this is a very rough take on an approach that would provide a limited form of
protection against downgrade attack. It's unclear at this point whether the additional effort (and
modest operational cost) is worthwhile.

The mechanism described in this specification is trivial to mount an active attack against, for two
reasons:

- A client that doesn't perform authentication is an easy victim of server impersonation, through
man-in-the-middle attacks.

- A client that is willing to use HTTP over cleartext to resolve the resource will do so if access
to any TLS-enabled alternative services is blocked at the network layer.

Given that the primary goal of this specification is to prevent passive attacks, these are not
critical failings (especially considering the alternative - HTTP over cleartext). However, a modest
form of protection against active attacks can be provided for clients on subsequent connections.

When an alternative service is able to commit to providing service for a particular origin over TLS
for a bounded period of time, clients can choose to rely upon its availability, failing when it
cannot be contacted. Effectively, this makes the choice to use a secured protocol "sticky" in the
client.


## The HTTP-TLS Header Field

A alternative service can make this commitment by sending a `HTTP-TLS` header field, described here
using the '#' ABNF extension defined in Section 7 of {{RFC7230}}:

~~~ abnf2616
    HTTP-TLS     = 1#parameter
~~~

When it appears in a HTTP response from a strongly authenticated alternative service, this header
field indicates that the availability of the origin through TLS-protected alternative services is
"sticky", and that the client MUST NOT fall back to cleartext protocols while this information is
considered fresh.

For example:

~~~ example
    GET /index.html HTTP/1.1
    Host: example.com
~~~

~~~ example
    HTTP/1.1 200 OK
    Content-Type: text/html
    Cache-Control: max-age=600
    Age: 30
    Date: Thu, 1 May 2014 16:20:09 GMT
    HTTP-TLS: ma=3600
~~~

This header field creates a commitment from the origin {{RFC6454}} of the associated resource (in
the example, `http://example.com`).  For the duration of the commitment, clients SHOULD strongly
authenticate the server for all subsequent requests made to that origin, though this creates some
risks for clients (see {{pinrisks}}).

Authentication for HTTP over TLS is described in Section 3.1 of {{RFC2818}}, noting the additional
requirements in Section 2.1 of {{I-D.ietf-httpbis-alt-svc}}. The header field MUST be ignored if
strong authentication fails; otherwise, an attacker could create a persistent denial of service by
falsifying a commitment.

The commitment to use authenticated TLS persists for a period determined by the value of the `ma`
parameter. See Section 4.2.3 of {{RFC7234}} for details of determining response age.

~~~ abnf2616
    ma-parameter     = delta-seconds
~~~

The commitment made by the `HTTP-TLS` header field applies only to the origin of the resource that
generates the `HTTP-TLS` header field.

Requests for an origin that has a persisted, unexpired value for `HTTP-TLS` MUST fail if they cannot
be made over an authenticated TLS connection.

Note that the commitment is not bound to a particular alternative service.  Clients SHOULD use
alternative services that they become aware of.  However, clients MUST NOT use an unauthenticated
alternative service for an origin with this commitment.  Where there is an active commitment,
clients MAY instead ignore advertisements for unsecured alternatives services.


## Operational Considerations {#pinrisks}

To avoid situations where a persisted value of `HTTP-TLS` causes a client to be unable to contact a
site, clients SHOULD limit the time that a value is persisted for a given origin. A lower limit
might be appropriate for initial observations of `HTTP-TLS`; the certainty that a site has set a
correct value - and the corresponding limit on persistence - can increase as the value is seen more
over time.

Once a server has indicated that it will support authenticated TLS, a client MAY use key pinning
{{RFC7469}} or any other mechanism that would otherwise be restricted to use
with `https` URIs, provided that the mechanism can be restricted to a single HTTP origin.



# IANA Considerations

This specification registers a Well-known URI {{RFC5785}}:

* URI Suffix: http-opportunistic
* Change Controller: IETF
* Specification Document(s): [this specification]
* Related Information:

# Security Considerations

## Security Indicators

User Agents MUST NOT provide any special security indicia when an `http` resource is acquired using
TLS. In particular, indicators that might suggest the same level of security as `https` MUST NOT be
used (e.g., using a "lock device").



## Downgrade Attacks {#downgrade}

A downgrade attack against the negotiation for TLS is possible. With the `HTTP-TLS` header field,
this is limited to occasions where clients have no prior information (see {{privacy}}), or when
persisted commitments have expired.

For example, because the `Alt-Svc` header field {{I-D.ietf-httpbis-alt-svc}} likely appears in an
unauthenticated and unencrypted channel, it is subject to downgrade by network attackers. In its
simplest form, an attacker that wants the connection to remain in the clear need only strip the
`Alt-Svc` header field from responses.

Downgrade attacks can be partially mitigated using the `HTTP-TLS` header field, because when it is
used, a client can avoid using cleartext to contact a supporting server. However, this only works
when a previous connection has been established without an active attacker present; a continuously
present active attacker can either prevent the client from ever using TLS, or offer its own
certificate.


## Privacy Considerations {#privacy}

Cached alternative services can be used to track clients over time; e.g., using a user-specific
hostname. Clearing the cache reduces the ability of servers to track clients; therefore clients
MUST clear cached alternative service information when clearing other origin-based state (i.e.,
cookies).


## Confusion Regarding Request Scheme

Many existing HTTP/1.1 implementations use the presence or absence of TLS in the stack to determine
whether requests are for `http` or `https` resources.  This is necessary in many cases because the
most common form of an HTTP/1.1 request does not carry an explicit indication of the URI scheme.

HTTP/1.1 MUST NOT be used for opportunistically secured requests.

Some HTTP/1.1 implementations use ambient signals to determine if a request is for an `https`
resource.  For example, implementations might look for TLS on the stack or a port number of 443.  An
implementation that supports opportunistically secured requests SHOULD suppress these signals if
there is any potential for confusion.


--- back

# Acknowledgements

Thanks to Patrick McManus, Eliot Lear, Stephen Farrell, Guy Podjarny, Stephen Ludin, Erik Nygren,
Paul Hoffman, Adam Langley, Eric Rescorla and Richard Barnes for their feedback and suggestions.
