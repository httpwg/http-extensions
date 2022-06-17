---
title: "Cookies: HTTP State Management Mechanism"
docname: draft-ietf-httpbis-rfc6265bis-latest
date: {DATE}
category: std
obsoletes: 6265

ipr: pre5378Trust200902
area: Applications and Real-Time
workgroup: HTTP
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline]
stand_alone: yes #_
smart_quotes: no

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/6265bis
github-issue-label: 6265bis

author:
-
  ins: L. Chen
  name: Lily Chen
  role: editor
  organization: Google LLC
  email: chlily@google.com
-
  ins: S. Englehardt
  name: Steven Englehardt
  role: editor
  organization: Mozilla
  email: senglehardt@mozilla.com
-
  ins: M. West
  name: Mike West
  role: editor
  organization: Google LLC
  email: mkwst@google.com
  uri: https://mikewest.org/
-
  ins: J. Wilander
  name: John Wilander
  role: editor
  organization: Apple, Inc
  email: wilander@apple.com

normative:
  RFC1034:
  RFC1123:
  RFC2119:
  RFC3490:
    override: yes
    title: "Internationalizing Domain Names in Applications (IDNA)"
    seriesinfo:
      RFC: 3490
    date: 2003-03
    author:
      -
        ins: P. Faltstrom
        ins: P. Hoffman
        ins: A. Costello
    ann: See {{idna-migration}} for an explanation why the normative reference to an obsoleted specification is needed.
  RFC4790:
  RFC5234:
  RFC5890:
  RFC6454:
  RFC8126:
  USASCII:
    title: "Coded Character Set -- 7-bit American Standard Code for Information Interchange"
    seriesinfo:
      ANSI: X3.4
    date: 1986
    author:
      organization: American National Standards Institute
  FETCH:
    target: https://fetch.spec.whatwg.org/
    title: Fetch
    author:
    -
      ins: A. van Kesteren
      name: Anne van Kesteren
      organization: Mozilla
  HTML:
    target: https://html.spec.whatwg.org/
    title: HTML
    author:
    -
      ins: I. Hickson
      name: Ian Hickson
      organization: Google, Inc.
    -
      ins: S. Pieters
      name: Simon Pieters
      organization: Opera
    -
      ins: A. van Kesteren
      name: Anne van Kesteren
      organization: Mozilla
    -
      ins: P. Jägenstedt
      name: Philip Jägenstedt
      organization: Opera
    -
      ins: D. Denicola
      name: Domenic Denicola
      organization: Google, Inc.
  DOM-DOCUMENT-COOKIE:
    target: https://html.spec.whatwg.org/#dom-document-cookie
    title: HTML - Living Standard
    date: 2021-05-18
    author:
    -
      org: WHATWG
  SAMESITE:
    target: https://html.spec.whatwg.org/#same-site
    title: HTML - Living Standard
    date: 2021-01-26
    author:
    -
      org: WHATWG
  SERVICE-WORKERS:
    target: http://www.w3.org/TR/service-workers/
    title: Service Workers
    author:
    -
      ins: A. Russell
      name: Alex Russell
    -
      ins: J. Song
      name: Jungkee Song
    -
      ins: J. Archibald
      name: Jake Archibald

informative:
  RFC2818:
  RFC3986:
  RFC6265:
  RFC4648:
  RFC3864:
  RFC5895:
  RFC6265:
  RFC7034:
  UTS46:
    target: http://unicode.org/reports/tr46/
    title: "Unicode IDNA Compatibility Processing"
    seriesinfo:
      UNICODE: "Unicode Technical Standards # 46"
    date: 2016-06
    author:
    -
      ins: M. Davis
      name: Mark Davis
    -
      ins: M. Suignard
      name: Michel Suignard
  CSRF:
    target: http://portal.acm.org/citation.cfm?id=1455770.1455782
    title: Robust Defenses for Cross-Site Request Forgery
    date: 2008-10
    author:
    -
      ins: A. Barth
      name: Adam Barth
    -
      ins: C. Jackson
    -
      ins: J. Mitchell
    seriesinfo:
      DOI: 10.1145/1455770.1455782
      ISBN: 978-1-59593-810-7
      ACM: "CCS '08: Proceedings of the 15th ACM conference on Computer and communications security (pages 75-88)"
  Aggarwal2010:
    author:
    -
      ins: G. Aggarwal
    -
      ins: E. Burzstein
    -
      ins: C. Jackson
    -
      ins: D. Boneh
    title: "An Analysis of Private Browsing Modes in Modern Browsers"
    date: 2010
    target: http://www.usenix.org/events/sec10/tech/full_papers/Aggarwal.pdf
  app-isolation:
    target: http://www.collinjackson.com/research/papers/appisolation.pdf
    title: App Isolation - Get the Security of Multiple Browsers with Just One
    author:
    -
      ins: E. Chen
      name: Eric Y. Chen
    -
      ins: J. Bau
      name: Jason Bau
    -
      ins: C. Reis
      name: Charles Reis
    -
      ins: A. Barth
      name: Adam Barth
    -
      ins: C. Jackson
      name: Collin Jackson
    date: 2011
  prerendering:
    target: https://www.chromium.org/developers/design-documents/prerender
    title: Chrome Prerendering
    author:
    -
      ins: C. Bentzel
      name: Chris Bentzel
  I-D.ietf-httpbis-cookie-alone:
  I-D.ietf-httpbis-cookie-prefixes:
  I-D.ietf-httpbis-cookie-same-site:
  PSL:
    target: https://publicsuffix.org/list/
    title: "Public Suffix List"

--- abstract

This document defines the HTTP Cookie and Set-Cookie header fields. These
header fields can be used by HTTP servers to store state (called cookies) at
HTTP user agents, letting the servers maintain a stateful session over the
mostly stateless HTTP protocol. Although cookies have many historical
infelicities that degrade their security and privacy, the Cookie and Set-Cookie
header fields are widely used on the Internet. This document obsoletes RFC
6265.

--- middle

# Introduction

This document defines the HTTP Cookie and Set-Cookie header fields. Using
the Set-Cookie header field, an HTTP server can pass name/value pairs and
associated metadata (called cookies) to a user agent. When the user agent makes
subsequent requests to the server, the user agent uses the metadata and other
information to determine whether to return the name/value pairs in the Cookie
header field.

Although simple on their surface, cookies have a number of complexities. For
example, the server indicates a scope for each cookie when sending it to the
user agent. The scope indicates the maximum amount of time in which the user
agent should return the cookie, the servers to which the user agent should
return the cookie, and the URI schemes for which the cookie is applicable.

For historical reasons, cookies contain a number of security and privacy
infelicities. For example, a server can indicate that a given cookie is
intended for "secure" connections, but the Secure attribute does not provide
integrity in the presence of an active network attacker. Similarly, cookies
for a given host are shared across all the ports on that host, even though the
usual "same-origin policy" used by web browsers isolates content retrieved via
different ports.

There are two audiences for this specification: developers of cookie-generating
servers and developers of cookie-consuming user agents.

To maximize interoperability with user agents, servers SHOULD limit themselves
to the well-behaved profile defined in {{sane-profile}} when generating cookies.

User agents MUST implement the more liberal processing rules defined in {{ua-requirements}}, in order to maximize interoperability with existing servers that do not
conform to the well-behaved profile defined in {{sane-profile}}.

This document specifies the syntax and semantics of these header fields as they are
actually used on the Internet. In particular, this document does not create
new syntax or semantics beyond those in use today. The recommendations for
cookie generation provided in {{sane-profile}} represent a preferred subset of current
server behavior, and even the more liberal cookie processing algorithm provided
in {{ua-requirements}} does not recommend all of the syntactic and semantic variations in
use today. Where some existing software differs from the recommended protocol
in significant ways, the document contains a note explaining the difference.

This document obsoletes {{RFC6265}}.

# Conventions

## Conformance Criteria

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in {{RFC2119}}.

Requirements phrased in the imperative as part of algorithms (such as "strip any
leading space characters" or "return false and abort these steps") are to be
interpreted with the meaning of the key word ("MUST", "SHOULD", "MAY", etc.)
used in introducing the algorithm.

Conformance requirements phrased as algorithms or specific steps can be
implemented in any manner, so long as the end result is equivalent. In
particular, the algorithms defined in this specification are intended to be
easy to understand and are not intended to be performant.

## Syntax Notation

This specification uses the Augmented Backus-Naur Form (ABNF) notation of
{{RFC5234}}.

The following core rules are included by reference, as defined in {{RFC5234}},
Appendix B.1: ALPHA (letters), CR (carriage return), CRLF (CR LF), CTLs
(controls), DIGIT (decimal 0-9), DQUOTE (double quote), HEXDIG
(hexadecimal 0-9/A-F/a-f), LF (line feed), NUL (null octet), OCTET (any
8-bit sequence of data except NUL), SP (space), HTAB (horizontal tab),
CHAR (any {{USASCII}} character), VCHAR (any visible {{USASCII}} character),
and WSP (whitespace).

The OWS (optional whitespace) and BWS (bad whitespace) rules are defined in
Section 5.6.3 of {{!HTTPSEM=I-D.ietf-httpbis-semantics}}.

## Terminology

The terms "user agent", "client", "server", "proxy", and "origin server" have
the same meaning as in the HTTP/1.1 specification ({{HTTPSEM}}, Section 3).

The request-host is the name of the host, as known by the user agent, to which
the user agent is sending an HTTP request or from which it is receiving an HTTP
response (i.e., the name of the host to which it sent the corresponding HTTP
request).

The term request-uri refers to "target URI" as defined in Section 7.1 of
{{HTTPSEM}}.

Two sequences of octets are said to case-insensitively match each other if and
only if they are equivalent under the i;ascii-casemap collation defined in
{{RFC4790}}.

The term string means a sequence of non-NUL octets.

The terms "active document", "ancestor browsing context", "browsing context",
"dedicated worker", "Document", "nested browsing context", "opaque origin",
"parent browsing context", "sandboxed origin browsing context flag", "shared
worker", "the worker's Documents", "top-level browsing context", and
"WorkerGlobalScope" are defined in {{HTML}}.

"Service Workers" are defined in the Service Workers specification
{{SERVICE-WORKERS}}.

The term "origin", the mechanism of deriving an origin from a URI, and the "the
same" matching algorithm for origins are defined in {{RFC6454}}.

"Safe" HTTP methods include `GET`, `HEAD`, `OPTIONS`, and `TRACE`, as defined
in Section 9.2.1 of {{HTTPSEM}}.

A domain's "public suffix" is the portion of a domain that is controlled by a
public registry, such as "com", "co.uk", and "pvt.k12.wy.us". A domain's
"registrable domain" is the domain's public suffix plus the label to its left.
That is, for `https://www.site.example`, the public suffix is `example`, and the
registrable domain is `site.example`. Whenever possible, user agents SHOULD
use an up-to-date public suffix list, such as the one maintained by the Mozilla
project at {{PSL}}.

The term "request", as well as a request's "client", "current url", "method",
"target browsing context", and "url list", are defined in {{FETCH}}.

The term "non-HTTP APIs" refers to non-HTTP mechanisms used to set and retrieve
cookies, such as a web browser API that exposes cookies to scripts.

# Overview

This section outlines a way for an origin server to send state information to a
user agent and for the user agent to return the state information to the origin
server.

To store state, the origin server includes a Set-Cookie header field in an HTTP
response. In subsequent requests, the user agent returns a Cookie request
header field to the origin server. The Cookie header field contains cookies the user agent
received in previous Set-Cookie header fields. The origin server is free to ignore
the Cookie header field or use its contents for an application-defined purpose.

Origin servers MAY send a Set-Cookie response header field with any response. An
origin server can include multiple Set-Cookie header fields in a single response.
The presence of a Cookie or a Set-Cookie header field does not preclude HTTP
caches from storing and reusing a response.

Origin servers SHOULD NOT fold multiple Set-Cookie header fields into a single
header field. The usual mechanism for folding HTTP headers fields (i.e., as
defined in Section 5.3 of {{HTTPSEM}}) might change the semantics of the Set-Cookie header
field because the %x2C (",") character is used by Set-Cookie in a way that
conflicts with such folding.

User agents MAY ignore Set-Cookie header fields based on response status codes or
the user agent's cookie policy (see {{ignoring-cookies}}).

## Examples

Using the Set-Cookie header field, a server can send the user agent a short string
in an HTTP response that the user agent will return in future HTTP requests that
are within the scope of the cookie. For example, the server can send the user
agent a "session identifier" named SID with the value 31d4d96e407aad42. The
user agent then returns the session identifier in subsequent requests.

~~~ example
== Server -> User Agent ==

Set-Cookie: SID=31d4d96e407aad42

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42
~~~

The server can alter the default scope of the cookie using the Path and
Domain attributes. For example, the server can instruct the user agent to
return the cookie to every path and every subdomain of site.example.

~~~ example
== Server -> User Agent ==

Set-Cookie: SID=31d4d96e407aad42; Path=/; Domain=site.example

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42
~~~

As shown in the next example, the server can store multiple cookies at the user
agent. For example, the server can store a session identifier as well as the
user's preferred language by returning two Set-Cookie header fields. Notice
that the server uses the Secure and HttpOnly attributes to provide
additional security protections for the more sensitive session identifier (see
{{sane-set-cookie-semantics}}).

~~~ example
== Server -> User Agent ==

Set-Cookie: SID=31d4d96e407aad42; Path=/; Secure; HttpOnly
Set-Cookie: lang=en-US; Path=/; Domain=site.example

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42; lang=en-US
~~~

Notice that the Cookie header field above contains two cookies, one named SID and
one named lang. If the server wishes the user agent to persist the cookie over
multiple "sessions" (e.g., user agent restarts), the server can specify an
expiration date in the Expires attribute. Note that the user agent might
delete the cookie before the expiration date if the user agent's cookie store
exceeds its quota or if the user manually deletes the server's cookie.

~~~ example
== Server -> User Agent ==

Set-Cookie: lang=en-US; Expires=Wed, 09 Jun 2021 10:18:14 GMT

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42; lang=en-US
~~~

Finally, to remove a cookie, the server returns a Set-Cookie header field with an
expiration date in the past. The server will be successful in removing the
cookie only if the Path and the Domain attribute in the Set-Cookie header field
match the values used when the cookie was created.

~~~ example
== Server -> User Agent ==

Set-Cookie: lang=; Expires=Sun, 06 Nov 1994 08:49:37 GMT

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42
~~~

# Server Requirements {#sane-profile}

This section describes the syntax and semantics of a well-behaved profile of the
Cookie and Set-Cookie header fields.

## Set-Cookie {#sane-set-cookie}

The Set-Cookie HTTP response header field is used to send cookies from the server to
the user agent.

### Syntax {#abnf-syntax}

Informally, the Set-Cookie response header field contains a cookie, which begins with a
name-value-pair, followed by zero or more attribute-value pairs. Servers
SHOULD NOT send Set-Cookie header fields that fail to conform to the following
grammar:

~~~ abnf
set-cookie        = set-cookie-string
set-cookie-string = BWS cookie-pair *( BWS ";" OWS cookie-av )
cookie-pair       = cookie-name BWS "=" BWS cookie-value
cookie-name       = 1*cookie-octet
cookie-value      = *cookie-octet / ( DQUOTE *cookie-octet DQUOTE )
cookie-octet      = %x21 / %x23-2B / %x2D-3A / %x3C-5B / %x5D-7E
                      ; US-ASCII characters excluding CTLs,
                      ; whitespace DQUOTE, comma, semicolon,
                      ; and backslash

cookie-av         = expires-av / max-age-av / domain-av /
                    path-av / secure-av / httponly-av /
                    samesite-av / extension-av
expires-av        = "Expires" BWS "=" BWS sane-cookie-date
sane-cookie-date  =
    <IMF-fixdate, defined in [HTTPSEM], Section 5.6.7>
max-age-av        = "Max-Age" BWS "=" BWS non-zero-digit *DIGIT
non-zero-digit    = %x31-39
                      ; digits 1 through 9
domain-av         = "Domain" BWS "=" BWS domain-value
domain-value      = <subdomain>
                      ; see details below
path-av           = "Path" BWS "=" BWS path-value
path-value        = *av-octet
secure-av         = "Secure"
httponly-av       = "HttpOnly"
samesite-av       = "SameSite" BWS "=" BWS samesite-value
samesite-value    = "Strict" / "Lax" / "None"
extension-av      = *av-octet
av-octet          = %x20-3A / %x3C-7E
                      ; any CHAR except CTLs or ";"
~~~

Note that some of the grammatical terms above reference documents that use
different grammatical notations than this document (which uses ABNF from
{{RFC5234}}).

The semantics of the cookie-value are not defined by this document.

To maximize compatibility with user agents, servers that wish to store arbitrary
data in a cookie-value SHOULD encode that data, for example, using Base64
{{RFC4648}}.

The domain-value is a subdomain as defined by {{RFC1034}}, Section 3.5, and
as enhanced by {{RFC1123}}, Section 2.1. Thus, domain-value is a string of
{{USASCII}} characters, such as one obtained by applying the "ToASCII" operation
defined in {{Section 4 of RFC3490}}.

Per the grammar above, the cookie-value MAY be wrapped in DQUOTE characters.
Note that in this case, the initial and trailing DQUOTE characters are not
stripped. They are part of the cookie-value, and will be included in Cookie
header fields sent to the server.

The portions of the set-cookie-string produced by the cookie-av term are
known as attributes. To maximize compatibility with user agents, servers SHOULD
NOT produce two attributes with the same name in the same set-cookie-string.
(See {{storage-model}} for how user agents handle this case.)

Servers SHOULD NOT include more than one Set-Cookie header field in the same
response with the same cookie-name. (See {{set-cookie}} for how user agents
handle this case.)

If a server sends multiple responses containing Set-Cookie header fields
concurrently to the user agent (e.g., when communicating with the user agent
over multiple sockets), these responses create a "race condition" that can lead
to unpredictable behavior.

NOTE: Some existing user agents differ in their interpretation of two-digit
years. To avoid compatibility issues, servers SHOULD use the rfc1123-date
format, which requires a four-digit year.

NOTE: Some user agents store and process dates in cookies as 32-bit UNIX time_t
values. Implementation bugs in the libraries supporting time_t processing on
some systems might cause such user agents to process dates after the year 2038
incorrectly.

### Semantics (Non-Normative) {#sane-set-cookie-semantics}

This section describes simplified semantics of the Set-Cookie header field. These
semantics are detailed enough to be useful for understanding the most common
uses of cookies by servers. The full semantics are described in {{ua-requirements}}.

When the user agent receives a Set-Cookie header field, the user agent stores the
cookie together with its attributes. Subsequently, when the user agent makes
an HTTP request, the user agent includes the applicable, non-expired cookies
in the Cookie header field.

If the user agent receives a new cookie with the same cookie-name,
domain-value, and path-value as a cookie that it has already stored, the
existing cookie is evicted and replaced with the new cookie. Notice that
servers can delete cookies by sending the user agent a new cookie with an
Expires attribute with a value in the past.

Unless the cookie's attributes indicate otherwise, the cookie is returned only
to the origin server (and not, for example, to any subdomains), and it expires
at the end of the current session (as defined by the user agent). User agents
ignore unrecognized cookie attributes (but not the entire cookie).

#### The Expires Attribute {#attribute-expires}

The Expires attribute indicates the maximum lifetime of the cookie,
represented as the date and time at which the cookie expires. The user agent is
not required to retain the cookie until the specified date has passed. In fact,
user agents often evict cookies due to memory pressure or privacy concerns.

The user agent MUST limit the maximum value of the Expires attribute.
The limit SHOULD NOT be greater than 400 days (34560000 seconds) in the future.
The RECOMMENDED limit is 400 days in the future, but the user agent MAY adjust
the limit (see {{cookie-policy}}).
Expires attributes that are greater than the limit MUST be reduced to the limit.

#### The Max-Age Attribute {#attribute-max-age}

The Max-Age attribute indicates the maximum lifetime of the cookie,
represented as the number of seconds until the cookie expires. The user agent is
not required to retain the cookie for the specified duration. In fact, user
agents often evict cookies due to memory pressure or privacy concerns.

The user agent MUST limit the maximum value of the Max-Age attribute.
The limit SHOULD NOT be greater than 400 days (34560000 seconds) in duration.
The RECOMMENDED limit is 400 days in duration, but the user agent MAY adjust
the limit (see {{cookie-policy}}).
Max-Age attributes that are greater than the limit MUST be reduced to the limit.

NOTE: Some existing user agents do not support the Max-Age attribute. User
agents that do not support the Max-Age attribute ignore the attribute.

If a cookie has both the Max-Age and the Expires attribute, the Max-Age
attribute has precedence and controls the expiration date of the cookie. If a
cookie has neither the Max-Age nor the Expires attribute, the user agent
will retain the cookie until "the current session is over" (as defined by the
user agent).

#### The Domain Attribute {#attribute-domain}

The Domain attribute specifies those hosts to which the cookie will be sent.
For example, if the value of the Domain attribute is "site.example", the user
agent will include the cookie in the Cookie header field when making HTTP requests to
site.example, www.site.example, and www.corp.site.example. (Note that a
leading %x2E ("."), if present, is ignored even though that character is not
permitted.)  If the server omits the Domain attribute, the user agent
will return the cookie only to the origin server.

WARNING: Some existing user agents treat an absent Domain attribute as if the
Domain attribute were present and contained the current host name. For
example, if site.example returns a Set-Cookie header field without a Domain
attribute, these user agents will erroneously send the cookie to
www.site.example as well.

The user agent will reject cookies unless the Domain attribute specifies a
scope for the cookie that would include the origin server. For example, the
user agent will accept a cookie with a Domain attribute of "site.example" or
of "foo.site.example" from foo.site.example, but the user agent will not accept
a cookie with a Domain attribute of "bar.site.example" or of
"baz.foo.site.example".

NOTE: For security reasons, many user agents are configured to reject Domain
attributes that correspond to "public suffixes". For example, some user
agents will reject Domain attributes of "com" or "co.uk". (See {{storage-model}} for
more information.)

#### The Path Attribute {#attribute-path}

The scope of each cookie is limited to a set of paths, controlled by the
Path attribute. If the server omits the Path attribute, the user agent will
use the "directory" of the request-uri's path component as the default value.
(See {{cookie-path}} for more details.)

The user agent will include the cookie in an HTTP request only if the path
portion of the request-uri matches (or is a subdirectory of) the cookie's
Path attribute, where the %x2F ("/") character is interpreted as a directory
separator.

Although seemingly useful for isolating cookies between different paths within
a given host, the Path attribute cannot be relied upon for security (see
{{security-considerations}}).

#### The Secure Attribute {#attribute-secure}

The Secure attribute limits the scope of the cookie to "secure" channels
(where "secure" is defined by the user agent). When a cookie has the Secure
attribute, the user agent will include the cookie in an HTTP request only if
the request is transmitted over a secure channel (typically HTTP over Transport
Layer Security (TLS) {{RFC2818}}).

#### The HttpOnly Attribute {#attribute-httponly}

The HttpOnly attribute limits the scope of the cookie to HTTP requests. In
particular, the attribute instructs the user agent to omit the cookie when
providing access to cookies via non-HTTP APIs.

Note that the HttpOnly attribute is independent of the Secure attribute: a
cookie can have both the HttpOnly and the Secure attribute.

#### The SameSite Attribute {#attribute-samesite}

The "SameSite" attribute limits the scope of the cookie such that it will only
be attached to requests if those requests are same-site, as defined by the
algorithm in {{same-site-requests}}. For example, requests for
`https://site.example/sekrit-image` will attach same-site cookies if and only if
initiated from a context whose "site for cookies" is an origin with a scheme and
registered domain of "https" and "site.example" respectively.

If the "SameSite" attribute's value is "Strict", the cookie will only be sent
along with "same-site" requests. If the value is "Lax", the cookie will be sent
with same-site requests, and with "cross-site" top-level navigations, as
described in {{strict-lax}}. If the value is "None", the cookie will be sent
with same-site and cross-site requests. If the "SameSite" attribute's value is
something other than these three known keywords, the attribute's value will be
subject to a default enforcement mode that is equivalent to "Lax".

The "SameSite" attribute affects cookie creation as well as delivery. Cookies
which assert "SameSite=Lax" or "SameSite=Strict" cannot be set in responses to
cross-site subresource requests, or cross-site nested navigations. They can be
set along with any top-level navigation, cross-site or otherwise.

### Cookie Name Prefixes

{{weak-confidentiality}} and {{weak-integrity}} of this document spell out some of the drawbacks of cookies'
historical implementation. In particular, it is impossible for a server to have
confidence that a given cookie was set with a particular set of attributes. In
order to provide such confidence in a backwards-compatible way, two common sets
of requirements can be inferred from the first few characters of the cookie's
name.

The normative requirements for the prefixes described below are detailed in the
storage model algorithm defined in {{storage-model}}.

#### The "__Secure-" Prefix

If a cookie's name begins with a case-sensitive match for the string
`__Secure-`, then the cookie will have been set with a `Secure` attribute.

For example, the following `Set-Cookie` header field would be rejected by a conformant
user agent, as it does not have a `Secure` attribute.

~~~ example
Set-Cookie: __Secure-SID=12345; Domain=site.example
~~~

Whereas the following `Set-Cookie` header field would be accepted if set from a secure origin
(e.g. "https://site.example/"), and rejected otherwise:

~~~ example
Set-Cookie: __Secure-SID=12345; Domain=site.example; Secure
~~~

#### The "__Host-" Prefix

If a cookie's name begins with a case-sensitive match for the string
`__Host-`, then the cookie will have been set with a `Secure` attribute, a
`Path` attribute with a value of `/`, and no `Domain` attribute.

This combination yields a cookie that hews as closely as a cookie can to
treating the origin as a security boundary. The lack of a `Domain` attribute
ensures that the cookie's `host-only-flag` is true, locking the cookie to a
particular host, rather than allowing it to span subdomains. Setting the `Path`
to `/` means that the cookie is effective for the entire host, and won't be
overridden for specific paths. The `Secure` attribute ensures that the cookie
is unaltered by non-secure origins, and won't span protocols.

Ports are the only piece of the origin model that `__Host-` cookies continue
to ignore.

For example, the following cookies would always be rejected:

~~~ example
Set-Cookie: __Host-SID=12345
Set-Cookie: __Host-SID=12345; Secure
Set-Cookie: __Host-SID=12345; Domain=site.example
Set-Cookie: __Host-SID=12345; Domain=site.example; Path=/
Set-Cookie: __Host-SID=12345; Secure; Domain=site.example; Path=/
~~~

While the following would be accepted if set from a secure origin (e.g.
"https://site.example/"), and rejected otherwise:

~~~ example
Set-Cookie: __Host-SID=12345; Secure; Path=/
~~~

## Cookie {#sane-cookie}

### Syntax

The user agent sends stored cookies to the origin server in the Cookie header field.
If the server conforms to the requirements in {{sane-set-cookie}} (and the user agent
conforms to the requirements in {{ua-requirements}}), the user agent will send a Cookie
header field that conforms to the following grammar:

~~~ abnf
cookie        = cookie-string
cookie-string = cookie-pair *( ";" SP cookie-pair )
~~~

### Semantics

Each cookie-pair represents a cookie stored by the user agent. The
cookie-pair contains the cookie-name and cookie-value the user agent
received in the Set-Cookie header field.

Notice that the cookie attributes are not returned. In particular, the server
cannot determine from the Cookie  field alone when a cookie will expire, for
which hosts the cookie is valid, for which paths the cookie is valid, or
whether the cookie was set with the Secure or HttpOnly attributes.

The semantics of individual cookies in the Cookie header field are not defined by
this document. Servers are expected to imbue these cookies with
application-specific semantics.

Although cookies are serialized linearly in the Cookie header field, servers SHOULD
NOT rely upon the serialization order. In particular, if the Cookie header field
contains two cookies with the same name (e.g., that were set with different
Path or Domain attributes), servers SHOULD NOT rely upon the order in which
these cookies appear in the header field.

# User Agent Requirements {#ua-requirements}

This section specifies the Cookie and Set-Cookie header fields in sufficient
detail that a user agent implementing these requirements precisely can
interoperate with existing servers (even those that do not conform to the
well-behaved profile described in {{sane-profile}}).

A user agent could enforce more restrictions than those specified herein (e.g.,
restrictions specified by its cookie policy, described in {{cookie-policy}}).
However, such additional restrictions may reduce the likelihood that a user
agent will be able to interoperate with existing servers.

## Subcomponent Algorithms

This section defines some algorithms used by user agents to process specific
subcomponents of the Cookie and Set-Cookie header fields.

### Dates {#cookie-date}

The user agent MUST use an algorithm equivalent to the following algorithm to
parse a cookie-date. Note that the various boolean flags defined as a part
of the algorithm (i.e., found-time, found-day-of-month, found-month,
found-year) are initially "not set".

1.  Using the grammar below, divide the cookie-date into date-tokens.

    ~~~ abnf
    cookie-date     = *delimiter date-token-list *delimiter
    date-token-list = date-token *( 1*delimiter date-token )
    date-token      = 1*non-delimiter

    delimiter       = %x09 / %x20-2F / %x3B-40 / %x5B-60 / %x7B-7E
    non-delimiter   = %x00-08 / %x0A-1F / DIGIT / ":" / ALPHA
                      / %x7F-FF
    non-digit       = %x00-2F / %x3A-FF

    day-of-month    = 1*2DIGIT [ non-digit *OCTET ]
    month           = ( "jan" / "feb" / "mar" / "apr" /
                        "may" / "jun" / "jul" / "aug" /
                        "sep" / "oct" / "nov" / "dec" ) *OCTET
    year            = 2*4DIGIT [ non-digit *OCTET ]
    time            = hms-time [ non-digit *OCTET ]
    hms-time        = time-field ":" time-field ":" time-field
    time-field      = 1*2DIGIT
    ~~~

2.  Process each date-token sequentially in the order the date-tokens
    appear in the cookie-date:

    1. If the found-time flag is not set and the token matches the
        time production, set the found-time flag and set the hour-value,
        minute-value, and second-value to the numbers denoted by the digits
        in the date-token, respectively. Skip the remaining sub-steps and
        continue to the next date-token.

    2. If the found-day-of-month flag is not set and the date-token matches
        the day-of-month production, set the found-day-of-month flag and set
        the day-of-month-value to the number denoted by the date-token. Skip
        the remaining sub-steps and continue to the next date-token.

    3. If the found-month flag is not set and the date-token matches the
        month production, set the found-month flag and set the month-value
        to the month denoted by the date-token. Skip the remaining sub-steps
        and continue to the next date-token.

    4. If the found-year flag is not set and the date-token matches the
        year production, set the found-year flag and set the year-value to
        the number denoted by the date-token. Skip the remaining sub-steps
        and continue to the next date-token.

3.  If the year-value is greater than or equal to 70 and less than or equal to
    99, increment the year-value by 1900.

4.  If the year-value is greater than or equal to 0 and less than or equal to
    69, increment the year-value by 2000.

    1. NOTE: Some existing user agents interpret two-digit years differently.

5.  Abort these steps and fail to parse the cookie-date if:

    *  at least one of the found-day-of-month, found-month, found-year, or
       found-time flags is not set,

    *  the day-of-month-value is less than 1 or greater than 31,

    *  the year-value is less than 1601,

    *  the hour-value is greater than 23,

    *  the minute-value is greater than 59, or

    *  the second-value is greater than 59.

    (Note that leap seconds cannot be represented in this syntax.)

6.  Let the parsed-cookie-date be the date whose day-of-month, month,
    year, hour, minute, and second (in UTC) are the
    day-of-month-value, the month-value, the year-value, the hour-value,
    the minute-value, and the second-value, respectively. If no such date
    exists, abort these steps and fail to parse the cookie-date.

7.  Return the parsed-cookie-date as the result of this algorithm.

### Canonicalized Host Names

A canonicalized host name is the string generated by the following algorithm:

1.  Convert the host name to a sequence of individual domain name labels.

2.  Convert each label that is not a Non-Reserved LDH (NR-LDH) label, to an
    A-label (see Section 2.3.2.1 of {{RFC5890}} for the former and latter), or
    to a "punycode label" (a label resulting from the "ToASCII" conversion in
    Section 4 of {{RFC3490}}), as appropriate (see {{idna-migration}} of this
    specification).

3.  Concatenate the resulting labels, separated by a %x2E (".") character.

### Domain Matching

A string domain-matches a given domain string if at least one of the following
conditions hold:

*   The domain string and the string are identical. (Note that both the domain
    string and the string will have been canonicalized to lower case at this
    point.)

*   All of the following conditions hold:

    *   The domain string is a suffix of the string.

    *   The last character of the string that is not included in the domain
        string is a %x2E (".") character.

    *   The string is a host name (i.e., not an IP address).

### Paths and Path-Match {#cookie-path}

The user agent MUST use an algorithm equivalent to the following algorithm to
compute the default-path of a cookie:

1.  Let uri-path be the path portion of the request-uri if such a portion
    exists (and empty otherwise).

2.  If the uri-path is empty or if the first character of the uri-path is
    not a %x2F ("/") character, output %x2F ("/") and skip the remaining steps.

3.  If the uri-path contains no more than one %x2F ("/") character, output
    %x2F ("/") and skip the remaining step.

4.  Output the characters of the uri-path from the first character up to, but
    not including, the right-most %x2F ("/").

A request-path path-matches a given cookie-path if at least one of the
following conditions holds:

*   The cookie-path and the request-path are identical.

    Note that this differs from the rules in {{RFC3986}} for equivalence of the
    path component, and hence two equivalent paths can have different cookies.

*   The cookie-path is a prefix of the request-path, and the last character
    of the cookie-path is %x2F ("/").

*   The cookie-path is a prefix of the request-path, and the first character
    of the request-path that is not included in the cookie-path is a %x2F
    ("/") character.

## "Same-site" and "cross-site" Requests  {#same-site-requests}

Two origins are same-site if they satisfy the "same site" criteria defined in
{{SAMESITE}}. A request is "same-site" if the following criteria are true:

1.  The request is not the result of a cross-site redirect. That is,
    the origin of every url in the request's url list is same-site with the
    request's current url's origin.

2.  The request is not the result of a reload navigation triggered through a
    user interface element (as defined by the user agent; e.g., a request
    triggered by the user clicking a refresh button on a toolbar).

3.  The request's current url's origin is same-site with the request's
    client's "site for cookies" (which is an origin), or if the request has no
    client or the request's client is null.

Requests which are the result of a reload navigation triggered through a user
interface element are same-site if the reloaded document was originally
navigated to via a same-site request. A request that is not "same-site" is
instead "cross-site".

The request's client's "site for cookies" is calculated depending upon its
client's type, as described in the following subsections:

### Document-based requests {#document-requests}

The URI displayed in a user agent's address bar is the only security context
directly exposed to users, and therefore the only signal users can reasonably
rely upon to determine whether or not they trust a particular website. The
origin of that URI represents the context in which a user most likely believes
themselves to be interacting. We'll define this origin, the top-level browsing
context's active document's origin, as the "top-level origin".

For a document displayed in a top-level browsing context, we can stop here: the
document's "site for cookies" is the top-level origin.

For documents which are displayed in nested browsing contexts, we need to audit
the origins of each of a document's ancestor browsing contexts' active documents
in order to account for the "multiple-nested scenarios" described in Section 4
of {{RFC7034}}. A document's "site for cookies" is the top-level origin if and
only if the top-level origin is same-site with the document's origin, and with
each of the document's ancestor documents' origins. Otherwise its "site for
cookies" is an origin set to an opaque origin.

Given a Document (`document`), the following algorithm returns its "site for
cookies":

1.  Let `top-document` be the active document in `document`'s browsing context's
    top-level browsing context.

2.  Let `top-origin` be the origin of `top-document`'s URI if `top-document`'s
    sandboxed origin browsing context flag is set, and `top-document`'s origin
    otherwise.

3.  Let `documents` be a list containing `document` and each of `document`'s
    ancestor browsing contexts' active documents.

4.  For each `item` in `documents`:

    1.  Let `origin` be the origin of `item`'s URI if `item`'s sandboxed origin
        browsing context flag is set, and `item`'s origin otherwise.

    2.  If `origin` is not same-site with `top-origin`, return an origin set to
        an opaque origin.

5.  Return `top-origin`.

### Worker-based requests {#worker-requests}

Worker-driven requests aren't as clear-cut as document-driven requests, as
there isn't a clear link between a top-level browsing context and a worker.
This is especially true for Service Workers {{SERVICE-WORKERS}}, which may
execute code in the background, without any document visible at all.

Note: The descriptions below assume that workers must be same-origin with
the documents that instantiate them. If this invariant changes, we'll need to
take the worker's script's URI into account when determining their status.

#### Dedicated and Shared Workers {#dedicated-and-shared-requests}

Dedicated workers are simple, as each dedicated worker is bound to one and only
one document. Requests generated from a dedicated worker (via `importScripts`,
`XMLHttpRequest`, `fetch()`, etc) define their "site for cookies" as that
document's "site for cookies".

Shared workers may be bound to multiple documents at once. As it is quite
possible for those documents to have distinct "site for cookies" values, the
worker's "site for cookies" will be an origin set to an opaque origin in cases
where the values are not all same-site with the worker's origin, and the
worker's origin in cases where the values agree.

Given a WorkerGlobalScope (`worker`), the following algorithm returns its "site
for cookies":

1.  Let `site` be `worker`'s origin.

2.  For each `document` in `worker`'s Documents:

    1.  Let `document-site` be `document`'s "site for cookies" (as defined
        in {{document-requests}}).

    2.  If `document-site` is not same-site with `site`, return an origin
        set to an opaque origin.

3.  Return `site`.

#### Service Workers

Service Workers are more complicated, as they act as a completely separate
execution context with only tangential relationship to the Document which
registered them.

Requests which simply pass through a Service Worker will be handled as described
above: the request's client will be the Document or Worker which initiated the
request, and its "site for cookies" will be those defined in
{{document-requests}} and {{dedicated-and-shared-requests}}

Requests which are initiated by the Service Worker itself (via a direct call to
`fetch()`, for instance), on the other hand, will have a client which is a
ServiceWorkerGlobalScope. Its "site for cookies" will be the Service Worker's
URI's origin.

Given a ServiceWorkerGlobalScope (`worker`), the following algorithm returns its
"site for cookies":

1.  Return `worker`'s origin.

## Ignoring Set-Cookie Header Fields {#ignoring-cookies}

User agents MAY ignore Set-Cookie header fields contained in responses with 100-level
status codes or based on its cookie policy (see {{cookie-policy}}).

All other Set-Cookie header fields SHOULD be processed according to {{set-cookie}}.
That is, Set-Cookie header fields contained in responses with non-100-level status
codes (including those in responses with 400- and 500-level status codes)
SHOULD be processed unless ignored according to the user agent's cookie policy.

## The Set-Cookie Header Field {#set-cookie}

When a user agent receives a Set-Cookie header field in an HTTP response, the
user agent MAY ignore the Set-Cookie header field in its entirety
(see {{ignoring-cookies}}).

If the user agent does not ignore the Set-Cookie header field in its entirety,
the user agent MUST parse the field-value of the Set-Cookie header field as a
set-cookie-string (defined below).

NOTE: The algorithm below is more permissive than the grammar in {{sane-set-cookie}}.
For example, the algorithm strips leading and trailing whitespace from the
cookie name and value (but maintains internal whitespace), whereas the grammar
in {{sane-set-cookie}} forbids whitespace in these positions. In addition, the
algorithm below accommodates some characters that are not cookie-octets
according to the grammar in {{sane-set-cookie}}. User agents use this algorithm
so as to interoperate with servers that do not follow the recommendations in
{{sane-profile}}.

NOTE: As set-cookie-string may originate from a non-HTTP API, it is not
guaranteed to be free of CTL characters, so this algorithm handles them
explicitly. Horizontal tab (%x09) is excluded from the CTL characters that
lead to set-cookie-string rejection, as it is considered whitespace, which is
handled separately.

NOTE: The set-cookie-string may contain octet sequences that appear
percent-encoded as per {{Section 2.1 of RFC3986}}. However, a user agent
MUST NOT decode these sequences and instead parse the individual octets
as specified in this algorithm.

A user agent MUST use an algorithm equivalent to the following algorithm to
parse a set-cookie-string:

1.  If the set-cookie-string contains a %x00-08 / %x0A-1F / %x7F character
    (CTL characters excluding HTAB):
    Abort these steps and ignore the set-cookie-string entirely.

2.  If the set-cookie-string contains a %x3B (";") character:

    1.  The name-value-pair string consists of the characters up to, but not
        including, the first %x3B (";"), and the unparsed-attributes consist of
        the remainder of the set-cookie-string (including the %x3B (";") in
        question).

    Otherwise:

    1.  The name-value-pair string consists of all the characters contained in
        the set-cookie-string, and the unparsed-attributes is the empty
        string.

3.  If the name-value-pair string lacks a %x3D ("=") character, then the name
    string is empty, and the value string is the value of name-value-pair.

    Otherwise, the name string consists of the characters up to, but not
    including, the first %x3D ("=") character, and the (possibly empty) value
    string consists of the characters after the first %x3D ("=") character.

4.  Remove any leading or trailing WSP characters from the name string and the
    value string.

5.  If the sum of the lengths of the name string and the value string is more
    than 4096 octets, abort these steps and ignore the set-cookie-string entirely.

6.  The cookie-name is the name string, and the cookie-value is the value string.

The user agent MUST use an algorithm equivalent to the following algorithm to
parse the unparsed-attributes:

1.  If the unparsed-attributes string is empty, skip the rest of these steps.

2.  Discard the first character of the unparsed-attributes (which will be a
    %x3B (";") character).

3.  If the remaining unparsed-attributes contains a %x3B (";") character:

    1.  Consume the characters of the unparsed-attributes up to, but not
        including, the first %x3B (";") character.

    Otherwise:

    1. Consume the remainder of the unparsed-attributes.

    Let the cookie-av string be the characters consumed in this step.

4.  If the cookie-av string contains a %x3D ("=") character:

    1.  The (possibly empty) attribute-name string consists of the characters
        up to, but not including, the first %x3D ("=") character, and the
        (possibly empty) attribute-value string consists of the characters
        after the first %x3D ("=") character.

    Otherwise:

    1.  The attribute-name string consists of the entire cookie-av string,
        and the attribute-value string is empty.

5.  Remove any leading or trailing WSP characters from the attribute-name
    string and the attribute-value string.

6.  If the attribute-value is longer than 1024 octets, ignore the cookie-av
    string and return to Step 1 of this algorithm.

7.  Process the attribute-name and attribute-value according to the
    requirements in the following subsections. (Notice that attributes with
    unrecognized attribute-names are ignored.)

8.  Return to Step 1 of this algorithm.

When the user agent finishes parsing the set-cookie-string, the user agent is
said to "receive a cookie" from the request-uri with name cookie-name,
value cookie-value, and attributes cookie-attribute-list. (See {{storage-model}}
for additional requirements triggered by receiving a cookie.)

### The Expires Attribute

If the attribute-name case-insensitively matches the string "Expires", the
user agent MUST process the cookie-av as follows.

1.  Let the expiry-time be the result of parsing the attribute-value as
    cookie-date (see {{cookie-date}}).

2.  If the attribute-value failed to parse as a cookie date, ignore the
    cookie-av.

3.  Let cookie-age-limit be the maximum age of the cookie (which SHOULD be 400 days
    in the future or sooner, see {{attribute-expires}}).

4.  If the expiry-time is more than cookie-age-limit, the user agent MUST set the
    expiry time to cookie-age-limit in seconds.

5.  If the expiry-time is earlier than the earliest date the user agent can
    represent, the user agent MAY replace the expiry-time with the earliest
    representable date.

6.  Append an attribute to the cookie-attribute-list with an attribute-name
    of Expires and an attribute-value of expiry-time.

### The Max-Age Attribute

If the attribute-name case-insensitively matches the string "Max-Age", the
user agent MUST process the cookie-av as follows.

1.  If the first character of the attribute-value is not a DIGIT or a "-"
    character, ignore the cookie-av.

2.  If the remainder of attribute-value contains a non-DIGIT character, ignore
    the cookie-av.

3.  Let delta-seconds be the attribute-value converted to an integer.

4.  Let cookie-age-limit be the maximum age of the cookie (which SHOULD be 400 days
    or less, see {{attribute-max-age}}).

5.  Set delta-seconds to the smaller of its present value and cookie-age-limit.

6.  If delta-seconds is less than or equal to zero (0), let expiry-time be
    the earliest representable date and time. Otherwise, let the expiry-time
    be the current date and time plus delta-seconds seconds.

7.  Append an attribute to the cookie-attribute-list with an attribute-name
    of Max-Age and an attribute-value of expiry-time.

### The Domain Attribute

If the attribute-name case-insensitively matches the string "Domain", the user
agent MUST process the cookie-av as follows.

1.  Let cookie-domain be the attribute-value.

2.  If cookie-domain starts with %x2E ("."), let cookie-domain be cookie-domain
    without its leading %x2E (".").

3.  Convert the cookie-domain to lower case.

4.  Append an attribute to the cookie-attribute-list with an attribute-name
    of Domain and an attribute-value of cookie-domain.

### The Path Attribute

If the attribute-name case-insensitively matches the string "Path", the user
agent MUST process the cookie-av as follows.

1.  If the attribute-value is empty or if the first character of the
    attribute-value is not %x2F ("/"):

    1.  Let cookie-path be the default-path.

    Otherwise:

    1.  Let cookie-path be the attribute-value.

2.  Append an attribute to the cookie-attribute-list with an attribute-name
    of Path and an attribute-value of cookie-path.

### The Secure Attribute

If the attribute-name case-insensitively matches the string "Secure", the
user agent MUST append an attribute to the cookie-attribute-list with an
attribute-name of Secure and an empty attribute-value.

### The HttpOnly Attribute

If the attribute-name case-insensitively matches the string "HttpOnly", the
user agent MUST append an attribute to the cookie-attribute-list with an
attribute-name of HttpOnly and an empty attribute-value.

### The SameSite Attribute

If the attribute-name case-insensitively matches the string "SameSite", the
user agent MUST process the cookie-av as follows:

1.  Let `enforcement` be "Default".

2.  If cookie-av's attribute-value is a case-insensitive match for "None",
    set `enforcement` to "None".

3.  If cookie-av's attribute-value is a case-insensitive match for "Strict",
    set `enforcement` to "Strict".

4.  If cookie-av's attribute-value is a case-insensitive match for "Lax", set
    `enforcement` to "Lax".

5.  Append an attribute to the cookie-attribute-list with an attribute-name
    of "SameSite" and an attribute-value of `enforcement`.

#### "Strict" and "Lax" enforcement {#strict-lax}

Same-site cookies in "Strict" enforcement mode will not be sent along with
top-level navigations which are triggered from a cross-site document context.
As discussed in {{top-level-navigations}}, this might or might not be compatible
with existing session management systems. In the interests of providing a
drop-in mechanism that mitigates the risk of CSRF attacks, developers may set
the `SameSite` attribute in a "Lax" enforcement mode that carves out an
exception which sends same-site cookies along with cross-site requests if and
only if they are top-level navigations which use a "safe" (in the {{HTTPSEM}}
sense) HTTP method. (Note that a request's method may be changed from POST
to GET for some redirects (see Sections 15.4.2 and 15.4.3 of {{HTTPSEM}}); in
these cases, a request's "safe"ness is determined based on the method of the
current redirect hop.)

Lax enforcement provides reasonable defense in depth against CSRF attacks that
rely on unsafe HTTP methods (like `POST`), but does not offer a robust defense
against CSRF as a general category of attack:

1. Attackers can still pop up new windows or trigger top-level navigations in
   order to create a "same-site" request (as described in {{document-requests}}), which
   is only a speedbump along the road to exploitation.

2. Features like `<link rel='prerender'>` {{prerendering}} can be exploited
   to create "same-site" requests without the risk of user detection.

When possible, developers should use a session management mechanism such as
that described in {{top-level-navigations}} to mitigate the risk of CSRF more
completely.

#### "Lax-Allowing-Unsafe" enforcement {#lax-allowing-unsafe}

As discussed in {{unsafe-top-level-requests}}, compatibility concerns may
necessitate the use of a "Lax-allowing-unsafe" enforcement mode that allows
cookies to be sent with a cross-site HTTP request if and only if it is a
top-level request, regardless of request method. That is, the
"Lax-allowing-unsafe" enforcement mode waives the requirement for the HTTP
request's method to be "safe" in the `SameSite` enforcement step of the
retrieval algorithm in {{retrieval-algorithm}}. (All cookies, regardless of
`SameSite` enforcement mode, may be set for top-level navigations, regardless of
HTTP request method, as specified in {{storage-model}}.)

"Lax-allowing-unsafe" is not a distinct value of the `SameSite` attribute.
Rather, user agents MAY apply "Lax-allowing-unsafe" enforcement only to cookies
that did not explicitly specify a `SameSite` attribute (i.e., those whose
same-site-flag was set to "Default" by default). To limit the scope of this
compatibility mode, user agents which apply "Lax-allowing-unsafe" enforcement
SHOULD restrict the enforcement to cookies which were created recently.
Deployment experience has shown a cookie age of 2 minutes or less to be a
reasonable limit.

If the user agent uses "Lax-allowing-unsafe" enforcement, it MUST apply the
following modification to the retrieval algorithm defined in
{{retrieval-algorithm}}:

Replace the condition in the penultimate bullet point of step 1 of the retrieval
algorithm reading

     * The HTTP request associated with the retrieval uses a "safe"
       method.

with

     * At least one of the following is true:

       1.  The HTTP request associated with the retrieval uses a "safe"
           method.

       2.  The cookie's same-site-flag is "Default" and the amount of
           time elapsed since the cookie's creation-time is at most a
           duration of the user agent's choosing.

## Storage Model {#storage-model}

The user agent stores the following fields about each cookie: name, value,
expiry-time, domain, path, creation-time, last-access-time,
persistent-flag, host-only-flag, secure-only-flag, http-only-flag,
and same-site-flag.

When the user agent "receives a cookie" from a request-uri with name
cookie-name, value cookie-value, and attributes cookie-attribute-list, the
user agent MUST process the cookie as follows:

1.  A user agent MAY ignore a received cookie in its entirety. See
    {{ignoring-cookies}}.

2. If cookie-name is empty and cookie-value is empty, abort these steps and
   ignore the cookie entirely.

3.  If the cookie-name or the cookie-value contains a
    %x00-08 / %x0A-1F / %x7F character (CTL characters excluding HTAB),
    abort these steps and ignore the cookie entirely.

4.  If the sum of the lengths of cookie-name and cookie-value is more than
    4096 octets, abort these steps and ignore the cookie entirely.

5.  Create a new cookie with name cookie-name, value cookie-value. Set the
    creation-time and the last-access-time to the current date and time.

6.  If the cookie-attribute-list contains an attribute with an attribute-name
    of "Max-Age":

    1.  Set the cookie's persistent-flag to true.

    2.  Set the cookie's expiry-time to attribute-value of the last
        attribute in the cookie-attribute-list with an attribute-name of
        "Max-Age".

    Otherwise, if the cookie-attribute-list contains an attribute with an
    attribute-name of "Expires" (and does not contain an attribute with an
    attribute-name of "Max-Age"):

    1.  Set the cookie's persistent-flag to true.

    2.  Set the cookie's expiry-time to attribute-value of the last
        attribute in the cookie-attribute-list with an attribute-name of
        "Expires".

    Otherwise:

    1.  Set the cookie's persistent-flag to false.

    2.  Set the cookie's expiry-time to the latest representable date.

7.  If the cookie-attribute-list contains an attribute with an
    attribute-name of "Domain":

    1.  Let the domain-attribute be the attribute-value of the last
        attribute in the cookie-attribute-list with both an
        attribute-name of "Domain" and an attribute-value whose
        length is no more than 1024 octets. (Note that a leading %x2E
        ("."), if present, is ignored even though that character is not
        permitted.)

    Otherwise:

    1.  Let the domain-attribute be the empty string.

8.  If the domain-attribute contains a character that is not in the range of {{USASCII}}
    characters, abort these steps and ignore the cookie entirely.

9.  If the user agent is configured to reject "public suffixes" and the
    domain-attribute is a public suffix:

    1.  If the domain-attribute is identical to the canonicalized
        request-host:

        1.  Let the domain-attribute be the empty string.

        Otherwise:

        1.  Abort these steps and ignore the cookie entirely.

    NOTE: This step prevents `attacker.example` from disrupting the integrity of
    `site.example` by setting a cookie with a Domain attribute of "example".

10. If the domain-attribute is non-empty:

    1.  If the canonicalized request-host does not domain-match the
        domain-attribute:

        1.  Abort these steps and ignore the cookie entirely.

        Otherwise:

        1.  Set the cookie's host-only-flag to false.

        2.  Set the cookie's domain to the domain-attribute.

    Otherwise:

    1.  Set the cookie's host-only-flag to true.

    2.  Set the cookie's domain to the canonicalized request-host.

11. If the cookie-attribute-list contains an attribute with an
    attribute-name of "Path", set the cookie's path to attribute-value of
    the last attribute in the cookie-attribute-list with both an
    attribute-name of "Path" and an attribute-value whose length is no
    more than 1024 octets. Otherwise, set the cookie's path to the
    default-path of the request-uri.

12. If the cookie-attribute-list contains an attribute with an
    attribute-name of "Secure", set the cookie's secure-only-flag to true.
    Otherwise, set the cookie's secure-only-flag to false.

13.  If the scheme component of the request-uri does not denote a "secure"
    protocol (as defined by the user agent), and the cookie's secure-only-flag
    is true, then abort these steps and ignore the cookie entirely.

14. If the cookie-attribute-list contains an attribute with an
    attribute-name of "HttpOnly", set the cookie's http-only-flag to true.
    Otherwise, set the cookie's http-only-flag to false.

15. If the cookie was received from a "non-HTTP" API and the cookie's
    http-only-flag is true, abort these steps and ignore the cookie entirely.

16. If the cookie's secure-only-flag is false, and the scheme component of
    request-uri does not denote a "secure" protocol, then abort these steps and
    ignore the cookie entirely if the cookie store contains one or more cookies
    that meet all of the following criteria:

    1.  Their name matches the name of the newly-created cookie.

    2.  Their secure-only-flag is true.

    3.  Their domain domain-matches the domain of the newly-created cookie, or
        vice-versa.

    4.  The path of the newly-created cookie path-matches the path of the
        existing cookie.

    Note: The path comparison is not symmetric, ensuring only that a
    newly-created, non-secure cookie does not overlay an existing secure
    cookie, providing some mitigation against cookie-fixing attacks. That is,
    given an existing secure cookie named 'a' with a path of '/login', a
    non-secure cookie named 'a' could be set for a path of '/' or '/foo', but
    not for a path of '/login' or '/login/en'.

17. If the cookie-attribute-list contains an attribute with an
    attribute-name of "SameSite", and an attribute-value of "Strict", "Lax", or
    "None", set the cookie's same-site-flag to the attribute-value of the last
    attribute in the cookie-attribute-list with an attribute-name of "SameSite".
    Otherwise, set the cookie's same-site-flag to "Default".

18. If the cookie's `same-site-flag` is not "None":

    1.  If the cookie was received from a "non-HTTP" API, and the API was called
        from a browsing context's active document whose "site for cookies" is
        not same-site with the top-level origin, then abort these steps and
        ignore the newly created cookie entirely.

    2.  If the cookie was received from a "same-site" request (as defined in
        {{same-site-requests}}), skip the remaining substeps and continue
        processing the cookie.

    3.  If the cookie was received from a request which is navigating a
        top-level browsing context {{HTML}} (e.g. if the request's "reserved
        client" is either `null` or an environment whose "target browsing
        context" is a top-level browing context), skip the remaining substeps
        and continue processing the cookie.

        Note: Top-level navigations can create a cookie with any `SameSite`
        value, even if the new cookie wouldn't have been sent along with
        the request had it already existed prior to the navigation.

    4.  Abort these steps and ignore the newly created cookie entirely.

19. If the cookie's "same-site-flag" is "None", abort these steps and ignore the
    cookie entirely unless the cookie's secure-only-flag is true.

20. If the cookie-name begins with a case-sensitive match for the string
    "__Secure-", abort these steps and ignore the cookie entirely unless the
    cookie's secure-only-flag is true.

21. If the cookie-name begins with a case-sensitive match for the string
    "__Host-", abort these steps and ignore the cookie entirely unless the
    cookie meets all the following criteria:

    1.  The cookie's secure-only-flag is true.

    2.  The cookie's host-only-flag is true.

    3.  The cookie-attribute-list contains an attribute with an attribute-name
        of "Path", and the cookie's path is `/`.

22. If the cookie store contains a cookie with the same name, domain,
    host-only-flag, and path as the newly-created cookie:

    1.  Let old-cookie be the existing cookie with the same name, domain,
        host-only-flag, and path as the newly-created cookie. (Notice that this
        algorithm maintains the invariant that there is at most one such
        cookie.)

    2.  If the newly-created cookie was received from a "non-HTTP" API and the
        old-cookie's http-only-flag is true, abort these steps and ignore the
        newly created cookie entirely.

    3.  Update the creation-time of the newly-created cookie to match the
        creation-time of the old-cookie.

    4.  Remove the old-cookie from the cookie store.

23. Insert the newly-created cookie into the cookie store.

A cookie is "expired" if the cookie has an expiry date in the past.

The user agent MUST evict all expired cookies from the cookie store if, at any
time, an expired cookie exists in the cookie store.

At any time, the user agent MAY "remove excess cookies" from the cookie store
if the number of cookies sharing a domain field exceeds some
implementation-defined upper bound (such as 50 cookies).

At any time, the user agent MAY "remove excess cookies" from the cookie store
if the cookie store exceeds some predetermined upper bound (such as 3000
cookies).

When the user agent removes excess cookies from the cookie store, the user
agent MUST evict cookies in the following priority order:

1.  Expired cookies.

2.  Cookies whose secure-only-flag is false, and which share a domain field
    with more than a predetermined number of other cookies.

3.  Cookies that share a domain field with more than a predetermined number of
    other cookies.

4.  All cookies.

If two cookies have the same removal priority, the user agent MUST evict the
cookie with the earliest last-access-time first.

When "the current session is over" (as defined by the user agent), the user
agent MUST remove from the cookie store all cookies with the persistent-flag
set to false.

## Retrieval Model {#retrieval-model}

This section defines how cookies are retrieved from a cookie store in the form
of a cookie-string. A "retrieval" is any event which requires generating a
cookie-string. For example, a retrieval may occur in order to build a Cookie
header field for an HTTP request, or may be required in order to return a
cookie-string from a call to a "non-HTTP" API that provides access to cookies. A
retrieval has an associated URI, same-site status, and type, which
are defined below depending on the type of retrieval.

### The Cookie Header Field {#cookie}

The user agent includes stored cookies in the Cookie HTTP request header field.

When the user agent generates an HTTP request, the user agent MUST NOT attach
more than one Cookie header field.

A user agent MAY omit the Cookie header field in its entirety.  For example, the
user agent might wish to block sending cookies during "third-party" requests
from setting cookies (see {{third-party-cookies}}).

If the user agent does attach a Cookie header field to an HTTP request, the
user agent MUST compute the cookie-string following the algorithm defined in
{{retrieval-algorithm}}, where the retrieval's URI is the request-uri, the
retrieval's same-site status is computed for the HTTP request as defined in
{{same-site-requests}}, and the retrieval's type is "HTTP".

### Non-HTTP APIs {#non-http}

The user agent MAY implement "non-HTTP" APIs that can be used to access
stored cookies.

A user agent MAY return an empty cookie-string in certain contexts, such as
when a retrieval occurs within a third-party context (see
{{third-party-cookies}}).

If a user agent does return cookies for a given call to a "non-HTTP" API with
an associated Document, then the user agent MUST compute the cookie-string
following the algorithm defined in {{retrieval-algorithm}}, where the
retrieval's URI is defined by the caller (see {{DOM-DOCUMENT-COOKIE}}), the
retrieval's same-site status is "same-site" if the Document's "site for
cookies" is same-site with the top-level origin as defined in
{{document-requests}} (otherwise it is "cross-site"), and the retrieval's type
is "non-HTTP".

### Retrieval Algorithm {#retrieval-algorithm}

Given a cookie store and a retrieval, the following algorithm returns a
cookie-string from a given cookie store.

1. Let cookie-list be the set of cookies from the cookie store that meets all
   of the following requirements:

   * Either:

     *   The cookie's host-only-flag is true and the canonicalized
         host of the retrieval's URI is identical to the cookie's domain.

     Or:

     *   The cookie's host-only-flag is false and the canonicalized
         host of the retrieval's URI domain-matches the cookie's domain.

   * The retrieval's URI's path path-matches the cookie's path.

   * If the cookie's secure-only-flag is true, then the retrieval's URI's
     scheme must denote a "secure" protocol (as defined by the user agent).

     NOTE: The notion of a "secure" protocol is not defined by this document.
     Typically, user agents consider a protocol secure if the protocol makes
     use of transport-layer security, such as SSL or TLS. For example, most
     user agents consider "https" to be a scheme that denotes a secure
     protocol.

   * If the cookie's http-only-flag is true, then exclude the cookie if the
     retrieval's type is "non-HTTP".

   * If the cookie's same-site-flag is not "None" and the retrieval's same-site
     status is "cross-site", then exclude the cookie unless all of the
     following conditions are met:

     * The retrieval's type is "HTTP".
     * The same-site-flag is "Lax" or "Default".
     * The HTTP request associated with the retrieval uses a "safe" method.
     * The target browsing context of the HTTP request associated with the
       retrieval is a top-level browsing context.

2. The user agent SHOULD sort the cookie-list in the following order:

   *  Cookies with longer paths are listed before cookies with shorter
      paths.

   *  Among cookies that have equal-length path fields, cookies with earlier
      creation-times are listed before cookies with later creation-times.

   NOTE: Not all user agents sort the cookie-list in this order, but this order
   reflects common practice when this document was written, and, historically,
   there have been servers that (erroneously) depended on this order.

3. Update the last-access-time of each cookie in the cookie-list to the
   current date and time.

4. Serialize the cookie-list into a cookie-string by processing each cookie
   in the cookie-list in order:

   1.  If the cookies' name is not empty, output the cookie's name followed by
       the %x3D ("=") character.

   2.  If the cookies' value is not empty, output the cookie's value.

   3.  If there is an unprocessed cookie in the cookie-list, output the
       characters %x3B and %x20 ("; ").

# Implementation Considerations

## Limits

Practical user agent implementations have limits on the number and size of
cookies that they can store. General-use user agents SHOULD provide each of the
following minimum capabilities:

*   At least 50 cookies per domain.

*   At least 3000 cookies total.

User agents MAY limit the maximum number of cookies they store, and may evict
any cookie at any time (whether at the request of the user or due to
implementation limitations).

Note that a limit on the maximum number of cookies also limits the total size of
the stored cookies, due to the length limits which MUST be enforced in
{{set-cookie}}.

Servers SHOULD use as few and as small cookies as possible to avoid reaching
these implementation limits and to minimize network bandwidth due to the
Cookie header field being included in every request.

Servers SHOULD gracefully degrade if the user agent fails to return one or more
cookies in the Cookie header field because the user agent might evict any cookie
at any time.

## Application Programming Interfaces

One reason the Cookie and Set-Cookie header fields use such esoteric syntax is
that many platforms (both in servers and user agents) provide a string-based
application programming interface (API) to cookies, requiring
application-layer programmers to generate and parse the syntax used by the
Cookie and Set-Cookie header fields, which many programmers have done incorrectly,
resulting in interoperability problems.

Instead of providing string-based APIs to cookies, platforms would be
well-served by providing more semantic APIs. It is beyond the scope of this
document to recommend specific API designs, but there are clear benefits to
accepting an abstract "Date" object instead of a serialized date string.

## IDNA Dependency and Migration {#idna-migration}

IDNA2008 {{RFC5890}} supersedes IDNA2003 {{RFC3490}}. However, there are
differences between the two specifications, and thus there can be differences
in processing (e.g., converting) domain name labels that have been registered
under one from those registered under the other. There will be a transition
period of some time during which IDNA2003-based domain name labels will exist
in the wild. User agents SHOULD implement IDNA2008 {{RFC5890}} and MAY
implement {{UTS46}} or {{RFC5895}} in order to facilitate their IDNA transition.
If a user agent does not implement IDNA2008, the user agent MUST implement
IDNA2003 {{RFC3490}}.

# Privacy Considerations

Cookies' primary privacy risk is their ability to correlate user activity. This
can happen on a single site, but is most problematic when activity is tracked across different,
seemingly unconnected Web sites to build a user profile.

Over time, this capability (warned against explicitly in {{?RFC2109}} and all of its successors)
has become widely used for varied reasons including:

* authenticating users across sites,
* assembling information on users,
* protecting against fraud and other forms of undesirable traffic,
* targeting advertisements at specific users or at users with specified attributes,
* measuring how often ads are shown to users, and
* recognizing when an ad resulted in a change in user behavior.

While not every use of cookies is necessarily problematic for privacy, their potential for abuse
has become a widespread concern in the Internet community and broader society. In response to these concerns, user agents
have actively constrained cookie functionality in various ways (as allowed and encouraged by
previous specifications), while avoiding disruption to features they judge desirable for the health
of the Web.

It is too early to declare consensus on which specific mechanism(s) should be used to mitigate cookies' privacy impact; user agents' ongoing changes to how they are handled are best characterised as experiments that
can provide input into that eventual consensus.

Instead, this document describes limited, general mitigations against the privacy risks associated
with cookies that enjoy wide deployment at the time of writing. It is expected that implementations
will continue to experiment and impose stricter, more well-defined limitations on cookies over
time. Future versions of this document might codify those mechanisms based upon deployment
experience. If functions that currently rely on cookies can be supported by separate, targeted
mechanisms, they might be documented in separate specifications and stricter limitations on cookies
might become feasible.

Note that cookies are not the only mechanism that can be used to track users across sites, so while
these mitigations are necessary to improve Web privacy, they are not sufficient on their own.


## Third-Party Cookies {#third-party-cookies}

A "third-party" or cross-site cookie is one that is associated with embedded content (such as
scripts, images, stylesheets, frames) that is obtained from a different server than the one that
hosts the primary resource (usually, the Web page that the user is viewing). Third-party cookies
are often used to correlate users' activity on different sites.

Because of their inherent privacy issues, most user agents now limit third-party cookies in a
variety of ways. Some completely block third-party cookies by refusing to process third-party
Set-Cookie header fields and refusing to send third-party Cookie header fields. Some partition
cookies based upon the first-party context, so that different cookies are sent depending on the
site being browsed. Some block cookies based upon user agent cookie policy and/or user controls.

While this document does not endorse or require a specific approach, it is RECOMMENDED that user
agents adopt a policy for third-party cookies that is as restrictive as compatibility constraints
permit. Consequently, resources cannot rely upon third-party cookies being treated consistently by
user agents for the foreseeable future.


## Cookie Policy {#cookie-policy}

User agents MAY enforce a cookie policy consisting of restrictions on how
cookies may be used or ignored (see {{ignoring-cookies}}).

A cookie policy may govern which domains or parties, as in first and third parties
(see {{third-party-cookies}}), for which the user agent will allow cookie access.
The policy can also define limits on cookie size, cookie expiry (see
{{attribute-expires}} and {{attribute-max-age}}), and the number of cookies per
domain or in total.

The recomended cookie expiry upper limit is 400 days. User agents may set
a lower limit to enforce shorter data retention timelines, or set the limit higher
to support longer retention when appropriate (e.g., server-to-server
communication over HTTPS).

The goal of a restrictive cookie policy is often to improve security or privacy.
User agents often allow users to change the cookie policy (see {{user-controls}}).

## User Controls {#user-controls}

User agents SHOULD provide users with a mechanism for managing the cookies
stored in the cookie store. For example, a user agent might let users delete
all cookies received during a specified time period or all the cookies related
to a particular domain. In addition, many user agents include a user interface
element that lets users examine the cookies stored in their cookie store.

User agents SHOULD provide users with a mechanism for disabling cookies. When
cookies are disabled, the user agent MUST NOT include a Cookie header field in
outbound HTTP requests and the user agent MUST NOT process Set-Cookie header fields
in inbound HTTP responses.

User agents MAY offer a way to change the cookie policy (see
{{cookie-policy}}).

User agents MAY provide users the option of preventing persistent storage of
cookies across sessions. When configured thusly, user agents MUST treat all
received cookies as if the persistent-flag were set to false. Some popular
user agents expose this functionality via "private browsing" mode
{{Aggarwal2010}}.

## Expiration Dates

Although servers can set the expiration date for cookies to the distant future,
most user agents do not actually retain cookies for multiple decades. Rather
than choosing gratuitously long expiration periods, servers SHOULD promote user
privacy by selecting reasonable cookie expiration periods based on the purpose
of the cookie. For example, a typical session identifier might reasonably be
set to expire in two weeks.

# Security Considerations {#security-considerations}

## Overview

Cookies have a number of security pitfalls. This section overviews a few of the
more salient issues.

In particular, cookies encourage developers to rely on ambient authority for
authentication, often becoming vulnerable to attacks such as cross-site request
forgery {{CSRF}}. Also, when storing session identifiers in cookies, developers
often create session fixation vulnerabilities.

Transport-layer encryption, such as that employed in HTTPS, is insufficient to
prevent a network attacker from obtaining or altering a victim's cookies because
the cookie protocol itself has various vulnerabilities (see "Weak Confidentiality"
and "Weak Integrity", below). In addition, by default, cookies do not provide
confidentiality or integrity from network attackers, even when used in conjunction
with HTTPS.

## Ambient Authority

A server that uses cookies to authenticate users can suffer security
vulnerabilities because some user agents let remote parties issue HTTP requests
from the user agent (e.g., via HTTP redirects or HTML forms). When issuing
those requests, user agents attach cookies even if the remote party does not
know the contents of the cookies, potentially letting the remote party exercise
authority at an unwary server.

Although this security concern goes by a number of names (e.g., cross-site
request forgery, confused deputy), the issue stems from cookies being a form of
ambient authority. Cookies encourage server operators to separate designation
(in the form of URLs) from authorization (in the form of cookies).
Consequently, the user agent might supply the authorization for a resource
designated by the attacker, possibly causing the server or its clients to
undertake actions designated by the attacker as though they were authorized by
the user.

Instead of using cookies for authorization, server operators might wish to
consider entangling designation and authorization by treating URLs as
capabilities. Instead of storing secrets in cookies, this approach stores
secrets in URLs, requiring the remote entity to supply the secret itself.
Although this approach is not a panacea, judicious application of these
principles can lead to more robust security.

## Clear Text

Unless sent over a secure channel (such as TLS), the information in the Cookie
and Set-Cookie header fields is transmitted in the clear.

1.  All sensitive information conveyed in these header fields is exposed to an
    eavesdropper.

2.  A malicious intermediary could alter the header fields as they travel in either
    direction, with unpredictable results.

3.  A malicious client could alter the Cookie header fields before transmission,
    with unpredictable results.

Servers SHOULD encrypt and sign the contents of cookies (using whatever format
the server desires) when transmitting them to the user agent (even when sending
the cookies over a secure channel). However, encrypting and signing cookie
contents does not prevent an attacker from transplanting a cookie from one user
agent to another or from replaying the cookie at a later time.

In addition to encrypting and signing the contents of every cookie, servers that
require a higher level of security SHOULD use the Cookie and Set-Cookie
header fields only over a secure channel. When using cookies over a secure channel,
servers SHOULD set the Secure attribute (see {{attribute-secure}}) for every
cookie. If a server does not set the Secure attribute, the protection
provided by the secure channel will be largely moot.

For example, consider a webmail server that stores a session identifier in a
cookie and is typically accessed over HTTPS. If the server does not set the
Secure attribute on its cookies, an active network attacker can intercept any
outbound HTTP request from the user agent and redirect that request to the
webmail server over HTTP. Even if the webmail server is not listening for HTTP
connections, the user agent will still include cookies in the request. The
active network attacker can intercept these cookies, replay them against the
server, and learn the contents of the user's email. If, instead, the server had
set the Secure attribute on its cookies, the user agent would not have
included the cookies in the clear-text request.

## Session Identifiers

Instead of storing session information directly in a cookie (where it might be
exposed to or replayed by an attacker), servers commonly store a nonce (or
"session identifier") in a cookie. When the server receives an HTTP request
with a nonce, the server can look up state information associated with the
cookie using the nonce as a key.

Using session identifier cookies limits the damage an attacker can cause if the
attacker learns the contents of a cookie because the nonce is useful only for
interacting with the server (unlike non-nonce cookie content, which might itself
be sensitive). Furthermore, using a single nonce prevents an attacker from
"splicing" together cookie content from two interactions with the server, which
could cause the server to behave unexpectedly.

Using session identifiers is not without risk. For example, the server SHOULD
take care to avoid "session fixation" vulnerabilities. A session fixation attack
proceeds in three steps. First, the attacker transplants a session identifier
from his or her user agent to the victim's user agent. Second, the victim uses
that session identifier to interact with the server, possibly imbuing the
session identifier with the user's credentials or confidential information.
Third, the attacker uses the session identifier to interact with server
directly, possibly obtaining the user's authority or confidential information.

## Weak Confidentiality {#weak-confidentiality}

Cookies do not provide isolation by port. If a cookie is readable by a service
running on one port, the cookie is also readable by a service running on another
port of the same server. If a cookie is writable by a service on one port, the
cookie is also writable by a service running on another port of the same server.
For this reason, servers SHOULD NOT both run mutually distrusting services on
different ports of the same host and use cookies to store security-sensitive
information.

Cookies do not provide isolation by scheme. Although most commonly used with
the http and https schemes, the cookies for a given host might also be
available to other schemes, such as ftp and gopher. Although this lack of
isolation by scheme is most apparent in non-HTTP APIs that permit access to
cookies (e.g., HTML's document.cookie API), the lack of isolation by scheme
is actually present in requirements for processing cookies themselves (e.g.,
consider retrieving a URI with the gopher scheme via HTTP).

Cookies do not always provide isolation by path. Although the network-level
protocol does not send cookies stored for one path to another, some user
agents expose cookies via non-HTTP APIs, such as HTML's document.cookie API.
Because some of these user agents (e.g., web browsers) do not isolate resources
received from different paths, a resource retrieved from one path might be able
to access cookies stored for another path.

## Weak Integrity {#weak-integrity}

Cookies do not provide integrity guarantees for sibling domains (and their
subdomains). For example, consider foo.site.example and bar.site.example. The
foo.site.example server can set a cookie with a Domain attribute of
"site.example" (possibly overwriting an existing "site.example" cookie set by
bar.site.example), and the user agent will include that cookie in HTTP requests
to bar.site.example. In the worst case, bar.site.example will be unable to
distinguish this cookie from a cookie it set itself. The foo.site.example
server might be able to leverage this ability to mount an attack against
bar.site.example.

Even though the Set-Cookie header field supports the Path attribute, the Path
attribute does not provide any integrity protection because the user agent
will accept an arbitrary Path attribute in a Set-Cookie header field. For
example, an HTTP response to a request for http://site.example/foo/bar can set
a cookie with a Path attribute of "/qux". Consequently, servers SHOULD NOT
both run mutually distrusting services on different paths of the same host and
use cookies to store security-sensitive information.

An active network attacker can also inject cookies into the Cookie header field
sent to https://site.example/ by impersonating a response from
http://site.example/ and injecting a Set-Cookie header field. The HTTPS server
at site.example will be unable to distinguish these cookies from cookies that
it set itself in an HTTPS response. An active network attacker might be able
to leverage this ability to mount an attack against site.example even if
site.example uses HTTPS exclusively.

Servers can partially mitigate these attacks by encrypting and signing the
contents of their cookies, or by naming the cookie with the `__Secure-` prefix.
However, using cryptography does not mitigate the issue completely because an
attacker can replay a cookie he or she received from the authentic site.example
server in the user's session, with unpredictable results.

Finally, an attacker might be able to force the user agent to delete cookies by
storing a large number of cookies. Once the user agent reaches its storage
limit, the user agent will be forced to evict some cookies. Servers SHOULD NOT
rely upon user agents retaining cookies.

## Reliance on DNS

Cookies rely upon the Domain Name System (DNS) for security. If the DNS is
partially or fully compromised, the cookie protocol might fail to provide the
security properties required by applications.

## SameSite Cookies

### Defense in depth

"SameSite" cookies offer a robust defense against CSRF attack when deployed in
strict mode, and when supported by the client. It is, however, prudent to ensure
that this designation is not the extent of a site's defense against CSRF, as
same-site navigations and submissions can certainly be executed in conjunction
with other attack vectors such as cross-site scripting.

Developers are strongly encouraged to deploy the usual server-side defenses
(CSRF tokens, ensuring that "safe" HTTP methods are idempotent, etc) to mitigate
the risk more fully.

Additionally, client-side techniques such as those described in
{{app-isolation}} may also prove effective against CSRF, and are certainly worth
exploring in combination with "SameSite" cookies.

### Top-level Navigations {#top-level-navigations}

Setting the `SameSite` attribute in "strict" mode provides robust defense in
depth against CSRF attacks, but has the potential to confuse users unless sites'
developers carefully ensure that their cookie-based session management systems
deal reasonably well with top-level navigations.

Consider the scenario in which a user reads their email at MegaCorp Inc's
webmail provider `https://site.example/`. They might expect that clicking on an
emailed link to `https://projects.example/secret/project` would show them the
secret project that they're authorized to see, but if `https://projects.example`
has marked their session cookies as `SameSite=Strict`, then this cross-site
navigation won't send them along with the request. `https://projects.example`
will render a 404 error to avoid leaking secret information, and the user will
be quite confused.

Developers can avoid this confusion by adopting a session management system that
relies on not one, but two cookies: one conceptually granting "read" access,
another granting "write" access. The latter could be marked as `SameSite=Strict`,
and its absence would prompt a reauthentication step before executing any
non-idempotent action. The former could be marked as `SameSite=Lax`, in
order to allow users access to data via top-level navigation, or
`SameSite=None`, to permit access in all contexts (including cross-site
embedded contexts).


### Mashups and Widgets

The `Lax` and `Strict` values for the `SameSite` attribute are inappropriate
for some important use-cases. In particular, note that content intended for
embedding in cross-site contexts (social networking widgets or commenting
services, for instance) will not have access to same-site cookies. Cookies
which are required in these situations should be marked with `SameSite=None`
to allow access in cross-site contexts.

Likewise, some forms of Single-Sign-On might require cookie-based authentication
in a cross-site context; these mechanisms will not function as intended with
same-site cookies and will also require `SameSite=None`.

### Server-controlled

SameSite cookies in and of themselves don't do anything to address the
general privacy concerns outlined in Section 7.1 of {{RFC6265}}. The "SameSite"
attribute is set by the server, and serves to mitigate the risk of certain kinds
of attacks that the server is worried about. The user is not involved in this
decision. Moreover, a number of side-channels exist which could allow a server
to link distinct requests even in the absence of cookies (for example, connection
and/or socket pooling between same-site and cross-site requests).

### Reload navigations

Requests issued for reloads triggered through user interface elements (such as a
refresh button on a toolbar) are same-site only if the reloaded document was
originally navigated to via a same-site request. This differs from the handling
of other reload navigations, which are always same-site if top-level, since the
source browsing context's active document is precisely the document being
reloaded.

This special handling of reloads triggered through a user interface element
avoids sending `SameSite` cookies on user-initiated reloads if they were
withheld on the original navigation (i.e., if the initial navigation were
cross-site). If the reload navigation were instead considered same-site, and
sent all the initially withheld `SameSite` cookies, the security benefits of
withholding the cookies in the first place would be nullified. This is
especially important given that the absence of `SameSite` cookies withheld on a
cross-site navigation request may lead to visible site breakage, prompting the
user to trigger a reload.

For example, suppose the user clicks on a link from `https://attacker.example/`
to `https://victim.example/`. This is a cross-site request, so `SameSite=Strict`
cookies are withheld. Suppose this causes `https://victim.example/` to appear
broken, because the site only displays its sensitive content if a particular
`SameSite` cookie is present in the request. The user, frustrated by the
unexpectedly broken site, presses refresh on their browser's toolbar. To now
consider the reload request same-site and send the initially withheld `SameSite`
cookie would defeat the purpose of withholding it in the first place, as the
reload navigation triggered through the user interface may replay the original
(potentially malicious) request. Thus, the reload request should be considered
cross-site, like the request that initially navigated to the page.

### Top-level requests with "unsafe" methods {#unsafe-top-level-requests}

The "Lax" enforcement mode described in {{strict-lax}} allows a cookie to be
sent with a cross-site HTTP request if and only if it is a top-level navigation
with a "safe" HTTP method. Implementation experience shows that this is
difficult to apply as the default behavior, as some sites may rely on cookies
not explicitly specifying a `SameSite` attribute being included on top-level
cross-site requests with "unsafe" HTTP methods (as was the case prior to the
introduction of the `SameSite` attribute).

For example, a login flow may involve a cross-site top-level `POST` request to
an endpoint which expects a cookie with login information. For such a cookie,
"Lax" enforcement is not appropriate, as it would cause the cookie to be
excluded due to the unsafe HTTP request method. On the other hand, "None"
enforcement would allow the cookie to be sent with all cross-site requests,
which may not be desirable due to the cookie's sensitive contents.

The "Lax-allowing-unsafe" enforcement mode described in {{lax-allowing-unsafe}}
retains some of the protections of "Lax" enforcement (as compared to "None")
while still allowing cookies to be sent cross-site with unsafe top-level
requests.

As a more permissive variant of "Lax" mode, "Lax-allowing-unsafe" mode
necessarily provides fewer protections against CSRF. Ultimately, the provision
of such an enforcement mode should be seen as a temporary, transitional measure
to ease adoption of "Lax" enforcement by default.

# IANA Considerations

## Cookie {#iana-cookie}

The permanent message header field registry (see {{RFC3864}}) needs to be
updated with the following registration:

Header field name:
: Cookie

Applicable protocol:
: http

Status:
: standard

Author/Change controller:
: IETF

Specification document:
: this specification ({{cookie}})

## Set-Cookie {#iana-set-cookie}

The permanent message header field registry (see {{RFC3864}}) needs to be
updated with the following registration:

Header field name:
: Set-Cookie

Applicable protocol:
: http

Status:
: standard

Author/Change controller:
: IETF

Specification document:
: this specification ({{set-cookie}})

## Cookie Attribute Registry

IANA is requested to create the "Cookie Attribute Registry", defining the
name space of attribute used to control cookies' behavior.
The registry should be maintained at
<https://www.iana.org/assignments/cookie-attribute-names>.

### Procedure

Each registered attribute name is associated with a description, and a
reference detailing how the attribute is to be processed and stored.

New registrations happen on a "RFC Required" basis (see Section 4.7 of
{{RFC8126}}). The attribute to be registered MUST match the `extension-av`
syntax defined in {{abnf-syntax}}. Note that attribute names are generally
defined in CamelCase, but technically accepted case-insensitively.

### Registration

The "Cookie Attribute Registry" should be created with the registrations below:

| Name     | Reference                               |
|----------:+----------------------------------------|
| Domain   | {{attribute-domain}} of this document   |
| Expires  | {{attribute-expires}} of this document  |
| HttpOnly | {{attribute-httponly}} of this document |
| Max-Age  | {{attribute-max-age}} of this document  |
| Path     | {{attribute-path}} of this document     |
| SameSite | {{attribute-samesite}} of this document |
| Secure   | {{attribute-secure}} of this document   |

--- back

# Changes

## draft-ietf-httpbis-rfc6265bis-00

*  Port {{RFC6265}} to Markdown. No (intentional) normative changes.

## draft-ietf-httpbis-rfc6265bis-01

*  Fixes to formatting caused by mistakes in the initial port to Markdown:

   *   <https://github.com/httpwg/http-extensions/issues/243>
   *   <https://github.com/httpwg/http-extensions/issues/246>

*  Addresses errata 3444 by updating the `path-value` and `extension-av`
   grammar, errata 4148 by updating the `day-of-month`, `year`, and `time`
   grammar, and errata 3663 by adding the requested note.
   <https://www.rfc-editor.org/errata_search.php?rfc=6265>

*  Dropped `Cookie2` and `Set-Cookie2` from the IANA Considerations section:
   <https://github.com/httpwg/http-extensions/issues/247>

*  Merged the recommendations from {{I-D.ietf-httpbis-cookie-alone}}, removing
   the ability for a non-secure origin to set cookies with a 'secure' flag, and
   to overwrite cookies whose 'secure' flag is true.

*  Merged the recommendations from {{I-D.ietf-httpbis-cookie-prefixes}}, adding
   `__Secure-` and `__Host-` cookie name prefix processing instructions.

## draft-ietf-httpbis-rfc6265bis-02

*  Merged the recommendations from {{I-D.ietf-httpbis-cookie-same-site}}, adding
   support for the `SameSite` attribute.

*  Closed a number of editorial bugs:

   *   Clarified address bar behavior for SameSite cookies:
       <https://github.com/httpwg/http-extensions/issues/201>

   *   Added the word "Cookies" to the document's name:
       <https://github.com/httpwg/http-extensions/issues/204>

   *   Clarified that the `__Host-` prefix requires an explicit `Path` attribute:
       <https://github.com/httpwg/http-extensions/issues/222>

   *   Expanded the options for dealing with third-party cookies to include a
       brief mention of partitioning based on first-party:
       <https://github.com/httpwg/http-extensions/issues/248>

   *   Noted that double-quotes in cookie values are part of the value, and are
       not stripped: <https://github.com/httpwg/http-extensions/issues/295>

   *   Fixed the "site for cookies" algorithm to return something that makes
       sense: <https://github.com/httpwg/http-extensions/issues/302>

## draft-ietf-httpbis-rfc6265bis-03

*  Clarified handling of invalid SameSite values:
   <https://github.com/httpwg/http-extensions/issues/389>

*  Reflect widespread implementation practice of including a cookie's
   `host-only-flag` when calculating its uniqueness:
   <https://github.com/httpwg/http-extensions/issues/199>

*  Introduced an explicit "None" value for the SameSite attribute:
   <https://github.com/httpwg/http-extensions/issues/788>

## draft-ietf-httpbis-rfc6265bis-04

*  Allow `SameSite` cookies to be set for all top-level navigations.
   <https://github.com/httpwg/http-extensions/issues/594>

*  Treat `Set-Cookie: token` as creating the cookie `("", "token")`:
   <https://github.com/httpwg/http-extensions/issues/159>

*  Reject cookies with neither name nor value (e.g. `Set-Cookie: =` and
   `Set-Cookie:`:  <https://github.com/httpwg/http-extensions/issues/159>

*  Clarified behavior of multiple `SameSite` attributes in a cookie string:
   <https://github.com/httpwg/http-extensions/issues/901>

## draft-ietf-httpbis-rfc6265bis-05

*  Typos and editorial fixes:
   <https://github.com/httpwg/http-extensions/pull/1035>,
   <https://github.com/httpwg/http-extensions/pull/1038>,
   <https://github.com/httpwg/http-extensions/pull/1040>,
   <https://github.com/httpwg/http-extensions/pull/1047>.

## draft-ietf-httpbis-rfc6265bis-06

*  Editorial fixes: <https://github.com/httpwg/http-extensions/issues/1059>,
   <https://github.com/httpwg/http-extensions/issues/1158>.

*  Created a registry for cookie attribute names:
   <https://github.com/httpwg/http-extensions/pull/1060>.

*  Tweaks to ABNF for `cookie-pair` and the `Cookie` header
   production: <https://github.com/httpwg/http-extensions/issues/1074>,
   <https://github.com/httpwg/http-extensions/issues/1119>.

*  Fixed serialization for nameless/valueless cookies:
   <https://github.com/httpwg/http-extensions/pull/1143>.

*  Converted a normative reference to Mozilla's Public Suffix List {{PSL}} into
   an informative reference:
   <https://github.com/httpwg/http-extensions/issues/1159>.

## draft-ietf-httpbis-rfc6265bis-07

*  Moved instruction to ignore cookies with empty cookie-name and cookie-value
   from {{set-cookie}} to {{storage-model}} to ensure that they apply to cookies
   created without parsing a cookie string:
   <https://github.com/httpwg/http-extensions/issues/1234>.

*  Add a default enforcement value to the `same-site-flag`, equivalent to
   "SameSite=Lax":
   <https://github.com/httpwg/http-extensions/pull/1325>.

*  Require a Secure attribute for "SameSite=None":
   <https://github.com/httpwg/http-extensions/pull/1323>.

* Consider scheme when running the same-site algorithm:
   <https://github.com/httpwg/http-extensions/pull/1324>.

## draft-ietf-httpbis-rfc6265bis-08

* Define "same-site" for reload navigation requests, e.g. those triggered via
  user interface elements:
  <https://github.com/httpwg/http-extensions/pull/1384>

* Consider redirects when defining same-site:
  <https://github.com/httpwg/http-extensions/pull/1348>

* Align on using HTML terminology for origins:
  <https://github.com/httpwg/http-extensions/pull/1416>

* Modify cookie parsing and creation algorithms in {{set-cookie}} and
  {{storage-model}} to explicitly handle control characters:
  <https://github.com/httpwg/http-extensions/pull/1420>

* Refactor cookie retrieval algorithm to support non-HTTP APIs:
  <https://github.com/httpwg/http-extensions/pull/1428>

* Define "Lax-allowing-unsafe" SameSite enforcement mode:
  <https://github.com/httpwg/http-extensions/pull/1435>

* Consistently use "header field" (vs 'header"):
  <https://github.com/httpwg/http-extensions/pull/1527>

## draft-ietf-httpbis-rfc6265bis-09

* Update cookie size requirements:
  <https://github.com/httpwg/http-extensions/pull/1563>

* Reject cookies with control characters:
  <https://github.com/httpwg/http-extensions/pull/1576>

* No longer treat horizontal tab as a control character:
  <https://github.com/httpwg/http-extensions/pull/1589>

* Specify empty domain attribute handling:
  <https://github.com/httpwg/http-extensions/pull/1709>

## draft-ietf-httpbis-rfc6265bis-10

* Standardize Max-Age/Expires upper bound:
  <https://github.com/httpwg/http-extensions/pull/1732>

# Acknowledgements
{:numbered="false"}
RFC 6265 was written by Adam Barth. This document is an update of RFC 6265,
adding features and aligning the specification with the reality of today’s
deployments. Here, we’re standing upon the shoulders of a giant since the
majority of the text is still Adam’s.
