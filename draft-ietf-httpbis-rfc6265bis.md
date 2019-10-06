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

author:
-
  ins: A. Barth
  name: Adam Barth
  organization: Google, Inc
  uri: https://www.adambarth.com/
-
  ins: M. West
  name: Mike West
  organization: Google, Inc
  email: mkwst@google.com
  uri: https://mikewest.org/

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
  RFC7230:
  RFC7231:
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
  PSL:
    target: https://publicsuffix.org/list/
    title: "Public Suffix List"

informative:
  RFC2818:
  RFC3986:
  RFC6265:
  RFC3629:
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

--- abstract

This document defines the HTTP Cookie and Set-Cookie header fields. These
header fields can be used by HTTP servers to store state (called cookies) at
HTTP user agents, letting the servers maintain a stateful session over the
mostly stateless HTTP protocol. Although cookies have many historical
infelicities that degrade their security and privacy, the Cookie and Set-Cookie
header fields are widely used on the Internet. This document obsoletes RFC
6265.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/6265bis>.

--- middle

# Introduction

TODO: Update to include explanation of global benefit of adding mechanisms
      to enable user agents to aid in compliance with EU Cookie Law, such
      as enabling standard placement and formatting of cookie banners per
      user agent and ability to consent in advance, and by category and
      domain, via settings or other means.
TODO: Add references to ePrivacy Directive, GDPR, and secondary sources.
      
TODO: Update to explain new consent requirement prior to storage by user agent.

This document defines the HTTP Cookie and Set-Cookie header fields. Using
the Set-Cookie header field, an HTTP server can pass name/value pairs and
associated metadata (called cookies) to a user agent. When the user agent makes
subsequent requests to the server, the user agent uses the metadata and other
information to determine whether to return the name/value pairs in the Cookie
header.

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

User agents MUST implement the more liberal processing rules defined in Section
5, in order to maximize interoperability with existing servers that do not
conform to the well-behaved profile defined in {{sane-profile}}.

TODO: Update to explain new syntax and semantics for EU Cookie Law mechanisms.

This document specifies the syntax and semantics of these headers as they are
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

The OWS (optional whitespace) rule is used where zero or more linear
whitespace characters MAY appear:

~~~ abnf
OWS            = *( [ obs-fold ] WSP )
                 ; "optional" whitespace
obs-fold       = CRLF
~~~

OWS SHOULD either not be produced or be produced as a single SP character.

## Terminology

TODO: Define first-party cookie.
TODO: Define third-party cookie.

The terms "user agent", "client", "server", "proxy", and "origin server" have
the same meaning as in the HTTP/1.1 specification ({{RFC7230}}, Section 2).

The request-host is the name of the host, as known by the user agent, to which
the user agent is sending an HTTP request or from which it is receiving an HTTP
response (i.e., the name of the host to which it sent the corresponding HTTP
request).

The term request-uri refers to "request-target" as defined in Section 5.3 of {{RFC7230}}.

Two sequences of octets are said to case-insensitively match each other if and
only if they are equivalent under the i;ascii-casemap collation defined in
{{RFC4790}}.

The term string means a sequence of non-NUL octets.

The terms "active document", "ancestor browsing context", "browsing context",
"dedicated worker", "Document", "WorkerGlobalScope", "sandboxed origin browsing
context flag", "parent browsing context", "shared worker", "the worker's
Documents", "nested browsing context", and "top-level browsing context" are
defined in {{HTML}}.

"Service Workers" are defined in the Service Workers specification
{{SERVICE-WORKERS}}.

The term "origin", the mechanism of deriving an origin from a URI, and the "the
same" matching algorithm for origins are defined in {{RFC6454}}.

"Safe" HTTP methods include `GET`, `HEAD`, `OPTIONS`, and `TRACE`, as defined
in Section 4.2.1 of {{RFC7231}}.

The term "public suffix" is defined in a note in Section 5.3 of {{RFC6265}} as
"a domain that is controlled by a public registry", and are also known as
"effective top-level domains" (eTLDs). For example, `example.com`'s public
suffix is `com`. User agents SHOULD use an up-to-date public suffix list,
such as the one maintained by Mozilla at {{PSL}}.

An origin's "registered domain" is the origin's host's public suffix plus the
label to its left. That is, for `https://www.example.com`, the public suffix is
`com`, and the registered domain is `example.com`. This concept is defined more
rigorously in {{PSL}}, and is also known as "effective top-level domain plus one"
(eTLD+1).

The term "request", as well as a request's "client", "current url", "method",
and "target browsing context", are defined in {{FETCH}}.

# Overview

This section outlines a way for an origin server to send state information to a
user agent and for the user agent to return the state information to the origin
server.

TODO: Update to explain new consent requirement prior to storage by user agent.

To store state, the origin server includes a Set-Cookie header in an HTTP
response. In subsequent requests, the user agent returns a Cookie request
header to the origin server. The Cookie header contains cookies the user agent
received in previous Set-Cookie headers. The origin server is free to ignore
the Cookie header or use its contents for an application-defined purpose.

Origin servers MAY send a Set-Cookie response header with any response. User
agents MAY ignore Set-Cookie headers contained in responses with 100-level
status codes but MUST process Set-Cookie headers contained in other responses
(including responses with 400- and 500-level status codes). An origin server
can include multiple Set-Cookie header fields in a single response. The
presence of a Cookie or a Set-Cookie header field does not preclude HTTP
caches from storing and reusing a response.

Origin servers SHOULD NOT fold multiple Set-Cookie header fields into a single
header field. The usual mechanism for folding HTTP headers fields (i.e., as
defined in Section 3.2.2 of {{RFC7230}}) might change the semantics of the Set-Cookie header
field because the %x2C (",") character is used by Set-Cookie in a way that
conflicts with such folding.

## Examples

TODO: Add examples using new EU Cookie Law mechanisms.

Using the Set-Cookie header, a server can send the user agent a short string
in an HTTP response that the user agent will return in future HTTP requests that
are within the scope of the cookie. For example, the server can send the user
agent a "session identifier" named SID with the value 31d4d96e407aad42. The
user agent then returns the session identifier in subsequent requests.

~~~
== Server -> User Agent ==

Set-Cookie: SID=31d4d96e407aad42

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42
~~~

The server can alter the default scope of the cookie using the Path and
Domain attributes. For example, the server can instruct the user agent to
return the cookie to every path and every subdomain of example.com.

~~~
== Server -> User Agent ==

Set-Cookie: SID=31d4d96e407aad42; Path=/; Domain=example.com

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42
~~~

As shown in the next example, the server can store multiple cookies at the user
agent. For example, the server can store a session identifier as well as the
user's preferred language by returning two Set-Cookie header fields. Notice
that the server uses the Secure and HttpOnly attributes to provide
additional security protections for the more sensitive session identifier (see
{{sane-set-cookie-semantics}}).

~~~
== Server -> User Agent ==

Set-Cookie: SID=31d4d96e407aad42; Path=/; Secure; HttpOnly
Set-Cookie: lang=en-US; Path=/; Domain=example.com

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42; lang=en-US
~~~

Notice that the Cookie header above contains two cookies, one named SID and
one named lang. If the server wishes the user agent to persist the cookie over
multiple "sessions" (e.g., user agent restarts), the server can specify an
expiration date in the Expires attribute. Note that the user agent might
delete the cookie before the expiration date if the user agent's cookie store
exceeds its quota or if the user manually deletes the server's cookie.

~~~
== Server -> User Agent ==

Set-Cookie: lang=en-US; Expires=Wed, 09 Jun 2021 10:18:14 GMT

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42; lang=en-US
~~~

Finally, to remove a cookie, the server returns a Set-Cookie header with an
expiration date in the past. The server will be successful in removing the
cookie only if the Path and the Domain attribute in the Set-Cookie header
match the values used when the cookie was created.

~~~
== Server -> User Agent ==

Set-Cookie: lang=; Expires=Sun, 06 Nov 1994 08:49:37 GMT

== User Agent -> Server ==

Cookie: SID=31d4d96e407aad42
~~~

# Server Requirements {#sane-profile}

This section describes the syntax and semantics of a well-behaved profile of the
Cookie and Set-Cookie headers.

## Set-Cookie {#sane-set-cookie}

TODO: Update to clarify this is a request now dependant on consent.

The Set-Cookie HTTP response header is used to send cookies from the server to
the user agent.

### Syntax

TODO: Handle unencoded DQUOTE embedded in purpose-value and policy-value.
TODO: Determine if purpose-value should have a max length.
TODO: Cookie banners must display a notice. Determine if this can be
      dynamically generated from the information provided, or if a
      mechanism need be created to supply the additional information
      to the user agent.

Informally, the Set-Cookie response header contains the header name
"Set-Cookie" followed by a ":" and a cookie. Each cookie begins with a
name-value-pair, followed by zero or more attribute-value pairs. Servers
SHOULD NOT send Set-Cookie headers that fail to conform to the following
grammar:

~~~ abnf
set-cookie-header = "Set-Cookie:" SP set-cookie-string
set-cookie-string = cookie-pair *( ";" SP cookie-av )
cookie-pair       = cookie-name "=" cookie-value
cookie-name       = token
cookie-value      = *cookie-octet / ( DQUOTE *cookie-octet DQUOTE )
cookie-octet      = %x21 / %x23-2B / %x2D-3A / %x3C-5B / %x5D-7E
                      ; US-ASCII characters excluding CTLs,
                      ; whitespace DQUOTE, comma, semicolon,
                      ; and backslash
token             = <token, defined in [RFC7230], Section 3.2.6>

cookie-av         = expires-av / max-age-av / domain-av /
                    path-av / secure-av / httponly-av /
                    samesite-av / category-av / purpose-av /
                    exempt-av / third-party-av / policy-av /
                    extension-av
expires-av        = "Expires=" sane-cookie-date
sane-cookie-date  =
    <IMF-fixdate, defined in [RFC7231], Section 7.1.1.1>
max-age-av        = "Max-Age=" non-zero-digit *DIGIT
                      ; In practice, both expires-av and max-age-av
                      ; are limited to dates representable by the
                      ; user agent.
non-zero-digit    = %x31-39
                      ; digits 1 through 9
domain-av         = "Domain=" domain-value
domain-value      = <subdomain>
                      ; defined in [RFC1034], Section 3.5, as
                      ; enhanced by [RFC1123], Section 2.1
path-av           = "Path=" path-value
path-value        = *av-octet
secure-av         = "Secure"
httponly-av       = "HttpOnly"
samesite-av       = "SameSite=" samesite-value
samesite-value    = "Strict" / "Lax" / "None"
category-av       = "Category=" category-value *( "," category-value)
category-value    = "Necessary" / "Preference" / "Analytical" /
                    "Marketing" / "Other"
purpose-av        = "Purpose=" purpose-value
purpose-value     = DQUOTE VCHAR *( SP VCHAR ) DQUOTE
exempt-av         = "Exempt"
third-party-av    = "ThirdParty"
policy-av         = "Policy=" policy-value
policy-value      = DQUOTE ( <http-URI> / <https-URI> ) DQUOTE
                      ; http-URI defined in [RFC7230], Section 2.7.1
                      ; https-URI defined in [RFC7230], Section 2.7.2
consent-av        = "Consent=" consent-value
consent-value     = <IMF-fixdate>
                      ; IMF-fixdate defined in [RFC7231], Section 7.1.1.1
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

Per the grammar above, the cookie-value MAY be wrapped in DQUOTE characters.
Note that in this case, the initial and trailing DQUOTE characters are not
stripped. They are part of the cookie-value, and will be included in Cookie
headers sent to the server.

The portions of the set-cookie-string produced by the cookie-av term are
known as attributes. To maximize compatibility with user agents, servers SHOULD
NOT produce two attributes with the same name in the same set-cookie-string.
(See {{storage-model}} for how user agents handle this case.)

Servers SHOULD NOT include more than one Set-Cookie header field in the same
response with the same cookie-name. (See {{set-cookie}} for how user agents
handle this case.)

If a server sends multiple responses containing Set-Cookie headers
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

TODO: Add note indicating it is the responsibility of the server to properly
      use attributes to ensure legal compliance, to confirm usage of such
      attributes satisfy such requirements, and to provide alternative
      mechanisms to achieve compliance with older and noncompliant
      user agents.

### Semantics (Non-Normative) {#sane-set-cookie-semantics}

This section describes simplified semantics of the Set-Cookie header. These
semantics are detailed enough to be useful for understanding the most common
uses of cookies by servers. The full semantics are described in {{ua-requirements}}.

TODO: Determine if it's necessary to create a mechanism whereby servers request
      consent, user agents confirm consent to servers, and user agents wait for
      confirmation of receipt before storing cookies, as servers are required
      to be able to prove consent was obtained; and there are scenarios where
      user agent will have obtained consent, and stored the cookie, but the
      server will never become aware of this.

When the user agent receives a Set-Cookie header, the user agent provides the
information in the category, purpose, and policy attributes to the user; and if the
third-party attribute is set, the user agent indicates to the user the cookie is a
third-party cookie. If the exempt attribute is set, the user agent stores the cookie
together with its attributes. If the exempt attribute is not set, and the consent
attribute is set, the user agent stores the cookie together with its attributes. If
the exempt attribute is not set, and the consent attribute is not set, the user
agent requests the user's consent, if not already provided by the user via settings
or another manner. If the user's consent is obtained, the user agent sets the consent
attribute and stores the cookie together with its attributes. Subsequently, when the
user agent makes an HTTP request, the user agent includes the applicable, non-expired
cookies in the Cookie header.

TODO: Determine how user agents can revoke consent.

If the user agent receives a new cookie with the same cookie-name,
domain-value, and path-value as a cookie that it has already stored, the
existing cookie is evicted and replaced with the new cookie. Notice that
servers can delete cookies by sending the user agent a new cookie with an
Expires attribute with a value in the past. Servers can revoke consent
by sending the user agent a new cookie without the consent attribute set.

Unless the cookie's attributes indicate otherwise, the cookie is returned only
to the origin server (and not, for example, to any subdomains), and it expires
at the end of the current session (as defined by the user agent). User agents
ignore unrecognized cookie attributes (but not the entire cookie).

#### The Expires Attribute

The Expires attribute indicates the maximum lifetime of the cookie,
represented as the date and time at which the cookie expires. The user agent is
not required to retain the cookie until the specified date has passed. In fact,
user agents often evict cookies due to memory pressure or privacy concerns.

#### The Max-Age Attribute

The Max-Age attribute indicates the maximum lifetime of the cookie,
represented as the number of seconds until the cookie expires. The user agent is
not required to retain the cookie for the specified duration. In fact, user
agents often evict cookies due to memory pressure or privacy concerns.

NOTE: Some existing user agents do not support the Max-Age attribute. User
agents that do not support the Max-Age attribute ignore the attribute.

If a cookie has both the Max-Age and the Expires attribute, the Max-Age
attribute has precedence and controls the expiration date of the cookie. If a
cookie has neither the Max-Age nor the Expires attribute, the user agent
will retain the cookie until "the current session is over" (as defined by the
user agent).

#### The Domain Attribute

The Domain attribute specifies those hosts to which the cookie will be sent.
For example, if the value of the Domain attribute is "example.com", the user
agent will include the cookie in the Cookie header when making HTTP requests to
example.com, www.example.com, and www.corp.example.com. (Note that a
leading %x2E ("."), if present, is ignored even though that character is not
permitted, but a trailing %x2E ("."), if present, will cause the user agent to
ignore the attribute.)  If the server omits the Domain attribute, the user
agent will return the cookie only to the origin server.

WARNING: Some existing user agents treat an absent Domain attribute as if the
Domain attribute were present and contained the current host name. For
example, if example.com returns a Set-Cookie header without a Domain
attribute, these user agents will erroneously send the cookie to
www.example.com as well.

The user agent will reject cookies unless the Domain attribute specifies a
scope for the cookie that would include the origin server. For example, the
user agent will accept a cookie with a Domain attribute of "example.com" or
of "foo.example.com" from foo.example.com, but the user agent will not accept
a cookie with a Domain attribute of "bar.example.com" or of
"baz.foo.example.com".

NOTE: For security reasons, many user agents are configured to reject Domain
attributes that correspond to "public suffixes". For example, some user
agents will reject Domain attributes of "com" or "co.uk". (See {{storage-model}} for
more information.)

#### The Path Attribute

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

#### The Secure Attribute {#sane-secure}

The Secure attribute limits the scope of the cookie to "secure" channels
(where "secure" is defined by the user agent). When a cookie has the Secure
attribute, the user agent will include the cookie in an HTTP request only if
the request is transmitted over a secure channel (typically HTTP over Transport
Layer Security (TLS) {{RFC2818}}).

Although seemingly useful for protecting cookies from active network attackers,
the Secure attribute protects only the cookie's confidentiality. An active
network attacker can overwrite Secure cookies from an insecure channel,
disrupting their integrity (see {{weak-integrity}} for more details).

#### The HttpOnly Attribute

The HttpOnly attribute limits the scope of the cookie to HTTP requests. In
particular, the attribute instructs the user agent to omit the cookie when
providing access to cookies via "non-HTTP" APIs (such as a web browser API that
exposes cookies to scripts).

Note that the HttpOnly attribute is independent of the Secure attribute: a
cookie can have both the HttpOnly and the Secure attribute.

#### The SameSite Attribute

The "SameSite" attribute limits the scope of the cookie such that it will only
be attached to requests if those requests are same-site, as defined by the
algorithm in {{same-site-requests}}. For example, requests for
`https://example.com/sekrit-image` will attach same-site cookies if and only if
initiated from a context whose "site for cookies" is "example.com".

If the "SameSite" attribute's value is "Strict", the cookie will only be sent
along with "same-site" requests. If the value is "Lax", the cookie will be sent
with same-site requests, and with "cross-site" top-level navigations, as
described in {{strict-lax}}. If the value is "None", the cookie will be sent
with same-site and cross-site requests. If the "SameSite" attribute's value is
something other than these three known keywords, the attribute's value will be
treated as "None".

#### The Category Attribute

TODO: Determine if all valid category values should be standardized in a
      seperate RFC, or if at least other, or additional values should be.
TODO: Require user agents to display the same, standard description of the
      categories defined here, or abandon this approach in favor of
      requiring categories and descriptions to be provided by servers (This
      may preclude advance user consent by category via settings.)

The Category attribute specifies the categories to which the cookie belongs.
Valid values are "Necessary", "Preference", "Analytical", "Marketing", and
"Other". Cookies can belong to one more than one categories, indicated by
a comma seperated list, without spaces, in the Categories attribute.

Necessary cookies enable basic functions, such as navigation or access; and
these cookies are strictly necesssary, because the application can not
function properly without the storage of these cookies by the user agent.
Preference cookies allow for persistence of user customization of
application appearance or behavior, such as color schemes, region, or
preferred language. Analytical cookies assist application administrators
understand how users interact with application, are used to agregate and
report information in an anonymous manner. Marketing cookies track users
across applications, usually for the purpose of displaying targeted
advertising. Other cookies are cookies that belong to a category other than
any of the categories listed here.

The Category attribute enables user agents to allow users to consent to
store of all cookies in a category, rather than individually.

#### The Purpose Attribute

TODO: Determine if all valid purpose values should be standardized.

The Purpose attribute describes the purpose of the cookie, and enables
user agents to provide the user with this information before requesting
the user's informed consent for the user agent to store the cookie.

#### The Exempt Attribute

The Exempt attribute informs the user agent if the user's consent must be
obtained prior to storing the cookie. If this attribute is set, the user
agent is advised that consent must be obtained. If this attribute is not
set, the user agent is advised that consent isn't necessary.

#### The Third-Party Attribute

The Third-Party attribute enables the user agent to indicate to the user
if the cookie is a third-party cookie. If this attribute is set, the user
agent is advised that the cookie is a third-party cookie. If this
attribute is not set, the use agent is advised that the cookie is a
first-party cookie, and not a third-party cookie.

#### The Policy Attribute

TODO: Determine if user agents should be required to make the link active.
TODO: Determine if user agents should attempt to locate, retrieve, and
      provide the policy content to the user directly.
TODO: Determine if the format for policy content should be standardized
      in another RFC.
TODO: Determine if the http-URI or https-URI values used are affected
      by the Secure or HttpOnly attributes, and how.

The Policy attribute is used to provide a URL that points to the
relevent cookie policy; and it enables user agents to either provide
the link to users or to locate, retrieve, and provide the policy content
to the user directly.

#### The Consent Attribute

TODO: Determine if it's feasible that not set can represent either
      consent not provided or consent revoked, depending on context.
TODO: Determine if this attribute should include a combination of
      action (unconfirmed, granted, revoked) and a time.

The Consent attribute is used to specify the time at which the user
provided consent for the user agent to store the cookie. If the Exempt
attribute is not set, and this attribute is not set, the user has not
provided consent, or the user has revoked their consent.

### Cookie Name Prefixes

TODO: Determine if prefixes can be used by user agents to signal
      acquisition and rejection of consent to servers.

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

For example, the following `Set-Cookie` header would be rejected by a conformant
user agent, as it does not have a `Secure` attribute.

~~~
Set-Cookie: __Secure-SID=12345; Domain=example.com
~~~

Whereas the following `Set-Cookie` header would be accepted:

~~~
Set-Cookie: __Secure-SID=12345; Domain=example.com; Secure
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

~~~
Set-Cookie: __Host-SID=12345
Set-Cookie: __Host-SID=12345; Secure
Set-Cookie: __Host-SID=12345; Domain=example.com
Set-Cookie: __Host-SID=12345; Domain=example.com; Path=/
Set-Cookie: __Host-SID=12345; Secure; Domain=example.com; Path=/
~~~

While the would be accepted if set from a secure origin (e.g.
"https://example.com/"), and rejected otherwise:

~~~
Set-Cookie: __Host-SID=12345; Secure; Path=/
~~~

## Cookie {#sane-cookie}

### Syntax

The user agent sends stored cookies to the origin server in the Cookie header.
If the server conforms to the requirements in {{sane-set-cookie}} (and the user agent
conforms to the requirements in {{ua-requirements}}), the user agent will send a Cookie
header that conforms to the following grammar:

~~~ abnf
cookie-header = "Cookie:" OWS cookie-string OWS
cookie-string = cookie-pair *( ";" SP cookie-pair )
~~~

### Semantics

Each cookie-pair represents a cookie stored by the user agent. The
cookie-pair contains the cookie-name and cookie-value the user agent
received in the Set-Cookie header.

Notice that the cookie attributes are not returned. In particular, the server
cannot determine from the Cookie header alone when a cookie will expire, for
which hosts the cookie is valid, for which paths the cookie is valid, or
whether the cookie was set with the Secure or HttpOnly attributes.

The semantics of individual cookies in the Cookie header are not defined by
this document. Servers are expected to imbue these cookies with
application-specific semantics.

Although cookies are serialized linearly in the Cookie header, servers SHOULD
NOT rely upon the serialization order. In particular, if the Cookie header
contains two cookies with the same name (e.g., that were set with different
Path or Domain attributes), servers SHOULD NOT rely upon the order in which
these cookies appear in the header.

# User Agent Requirements {#ua-requirements}

This section specifies the Cookie and Set-Cookie headers in sufficient
detail that a user agent implementing these requirements precisely can
interoperate with existing servers (even those that do not conform to the
well-behaved profile described in {{sane-profile}}).

A user agent could enforce more restrictions than those specified herein (e.g.,
for the sake of improved security); however, experiments have shown that such
strictness reduces the likelihood that a user agent will be able to interoperate
with existing servers.

## Subcomponent Algorithms

This section defines some algorithms used by user agents to process specific
subcomponents of the Cookie and Set-Cookie headers.

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
    non-delimiter   = %x00-08 / %x0A-1F / DIGIT / ":" / ALPHA / %x7F-FF
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
    exists (and empty otherwise). For example, if the request-uri contains
    just a path (and optional query string), then the uri-path is that path
    (without the %x3F ("?") character or query string), and if the request-uri
    contains a full absoluteURI, the uri-path is the path component of
    that URI.

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

A request is "same-site" if its target's URI's origin's registered domain
is an exact match for the request's client's "site for cookies", or if the
request has no client. The request is otherwise "cross-site".

For a given request ("request"), the following algorithm returns `same-site` or
`cross-site`:

1.  If `request`'s client is `null`, return `same-site`.

    Note that this is the case for navigation triggered by the user directly
    (e.g. by typing directly into a user agent's address bar).

2.  Let `site` be `request`'s client's "site for cookies" (as defined in the
    following sections).

3.  Let `target` be the registered domain of `request`'s current url.

4.  If `site` is an exact match for `target`, return `same-site`.

5.  Return `cross-site`.

The request's client's "site for cookies" is calculated depending upon its
client's type, as described in the following subsections:

### Document-based requests {#document-requests}

The URI displayed in a user agent's address bar is the only security context
directly exposed to users, and therefore the only signal users can reasonably
rely upon to determine whether or not they trust a particular website. The
registered domain of that URI's origin represents the context in which a user
most likely believes themselves to be interacting. We'll label this domain the
"top-level site".

For a document displayed in a top-level browsing context, we can stop here: the
document's "site for cookies" is the top-level site.

For documents which are displayed in nested browsing contexts, we need to audit
the origins of each of a document's ancestor browsing contexts' active documents
in order to account for the "multiple-nested scenarios" described in Section 4
of {{RFC7034}}. A document's "site for cookies" is the top-level site if and
only if the document and each of its ancestor documents' origins have the same
registered domain as the top-level site. Otherwise its "site for cookies" is
the empty string.

Given a Document (`document`), the following algorithm returns its "site for
cookies" (either a registered domain, or the empty string):

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

    2.  If `origin`'s host's registered domain is not an exact match for
        `top-origin`'s host's registered domain, return the empty string.

5.  Return `top-origin`'s host's registered domain.

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
possible for those documents to have distinct "site for cookie" values, the
worker's "site for cookies" will be the empty string in cases where the values
diverge, and the shared value in cases where the values agree.

Given a WorkerGlobalScope (`worker`), the following algorithm returns its "site
for cookies" (either a registered domain, or the empty string):

1.  Let `site` be `worker`'s origin's host's registered domain.

2.  For each `document` in `worker`'s Documents:

    1.  Let `document-site` be `document`'s "site for cookies" (as defined
        in {{document-requests}}).

    2.  If `document-site` is not an exact match for `site`, return the empty
        string.

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
ServiceWorkerGlobalScope. Its "site for cookies" will be the registered domain
of the Service Worker's URI.

Given a ServiceWorkerGlobalScope (`worker`), the following algorithm returns its
"site for cookies" (either a registered domain, or the empty string):

1.  Return `worker`'s origin's host's registered domain.

## The Set-Cookie Header {#set-cookie}

TODO: Determine how user agents should behave when not all required attributes
      enabling EU Cookie Law compliance are provided correctly.

When a user agent receives a Set-Cookie header field in an HTTP response, the
user agent MAY ignore the Set-Cookie header field in its entirety. For
example, the user agent might wish to block responses to "third-party" requests
from setting cookies (see {{third-party-cookies}}).

If the user agent does not ignore the Set-Cookie header field in its entirety,
the user agent MUST parse the field-value of the Set-Cookie header field as a
set-cookie-string (defined below).

NOTE: The algorithm below is more permissive than the grammar in {{sane-set-cookie}}.
For example, the algorithm strips leading and trailing whitespace from the
cookie name and value (but maintains internal whitespace), whereas the grammar
in {{sane-set-cookie}} forbids whitespace in these positions. User agents use this
algorithm so as to interoperate with servers that do not follow the
recommendations in {{sane-profile}}.

A user agent MUST use an algorithm equivalent to the following algorithm to
parse a set-cookie-string:

1.  If the set-cookie-string contains a %x3B (";") character:

    1.  The name-value-pair string consists of the characters up to, but not
        including, the first %x3B (";"), and the unparsed-attributes consist of
        the remainder of the set-cookie-string (including the %x3B (";") in
        question).

    Otherwise:

    1.  The name-value-pair string consists of all the characters contained in
        the set-cookie-string, and the unparsed-attributes is the empty
        string.

2.  If the name-value-pair string lacks a %x3D ("=") character, ignore the
    set-cookie-string entirely.

3.  The (possibly empty) name string consists of the characters up to, but not
    including, the first %x3D ("=") character, and the (possibly empty) value
    string consists of the characters after the first %x3D ("=") character.

4.  Remove any leading or trailing WSP characters from the name string and the
    value string.

5.  If the name string is empty, ignore the set-cookie-string entirely.

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

6.  Process the attribute-name and attribute-value according to the
    requirements in the following subsections. (Notice that attributes with
    unrecognized attribute-names are ignored.)

7.  Return to Step 1 of this algorithm.

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

3.  If the expiry-time is later than the last date the user agent can
    represent, the user agent MAY replace the expiry-time with the last
    representable date.

4.  If the expiry-time is earlier than the earliest date the user agent can
    represent, the user agent MAY replace the expiry-time with the earliest
    representable date.

5.  Append an attribute to the cookie-attribute-list with an attribute-name
    of Expires and an attribute-value of expiry-time.

### The Max-Age Attribute

If the attribute-name case-insensitively matches the string "Max-Age", the
user agent MUST process the cookie-av as follows.

1.  If the first character of the attribute-value is not a DIGIT or a "-"
    character, ignore the cookie-av.

2.  If the remainder of attribute-value contains a non-DIGIT character, ignore
    the cookie-av.

3.  Let delta-seconds be the attribute-value converted to an integer.

4.  If delta-seconds is less than or equal to zero (0), let expiry-time be
    the earliest representable date and time. Otherwise, let the expiry-time
    be the current date and time plus delta-seconds seconds.

5.  Append an attribute to the cookie-attribute-list with an attribute-name
    of Max-Age and an attribute-value of expiry-time.

### The Domain Attribute

If the attribute-name case-insensitively matches the string "Domain", the user
agent MUST process the cookie-av as follows.

1.  If the attribute-value is empty, the behavior is undefined. However, the
    user agent SHOULD ignore the cookie-av entirely.

2.  If the first character of the attribute-value string is %x2E ("."):

    1.  Let cookie-domain be the attribute-value without the leading %x2E
        (".") character.

    Otherwise:

    1. Let cookie-domain be the entire attribute-value.

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

1.  Let `enforcement` be "None".

2.  If cookie-av's attribute-value is a case-insensitive match for "Strict",
    set `enforcement` to "Strict".

3.  If cookie-av's attribute-value is a case-insensitive match for "Lax", set
    `enforcement` to "Lax".

4.  Append an attribute to the cookie-attribute-list with an attribute-name
    of "SameSite" and an attribute-value of `enforcement`.

Note: This algorithm maps the "None" value, as well as any unknown value, to
the "None" behavior, which is helpful for backwards compatibility when
introducing new variants.

### The Category Attribute

TODO: Require user agents not to store a cookie consented to by category,
      when the cookie is also member of other categories not consented to,
      unless the cookie is individually consented to.

If the attribute-name case-insensitively matches the string "Category", the
user agent MUST process the cookie-av as follows:

1.  If the attribute-value contains a %x2c (",") character:

    1.  The cookie-category string consists of the characters up to, but not
        including, the first %x2c (","), and the unparsed-category-values
        consist of the remainder of the attribute-value (including the
        %x2c (",") in question).

    Otherwise:

    1.  The cookie-category string consists of all the characters contained in
        the attribute-value, and the unparsed-category-values is the empty
        string.
        
2.  Remove any leading or trailing WSP characters from the cookie-category
    string.

3.  If the cookie-category is not a case-insensitive match for "Necessary",
    "Preference", "Analytical", "Marketing", or "Other":

    1.  Ignore the cookie-category.

    Otherwise:

    1.  Append an attribute to the cookie-attribute-list with an attribute-name
    of "Category" and an attribute-value of cookie-category.
    
The user agent MUST use an algorithm equivalent to the following algorithm to
parse the unparsed-category-values:

1.  If the unparsed-category-values string is empty, skip the rest of these
    steps.

2.  Discard the first character of the unparsed-category-values (which will be
    a %x2c (",") character).

3.  If the remaining unparsed-category-values contains a %x2c (",") character:

    1.  Consume the characters of the unparsed-category-values up to, but not
        including, the first %x2c (",") character.

    Otherwise:

    1. Consume the remainder of the unparsed-category-values.

    Let the cookie-category string be the characters consumed in this step.

4.  Remove any leading or trailing WSP characters from the cookie-category
    string.

5.  If the cookie-category is not a case-insensitive match for "Necessary",
    "Preference", "Analytical", "Marketing", or "Other":

    1.  Ignore the cookie-category.

    Otherwise:

    TODO: Properly append additional categories.

    1.  Append an attribute to the cookie-attribute-list with an
    attribute-name of "Category" and an attribute-value of cookie-category.

6.  Return to Step 1 of this algorithm.

### The Purpose Attribute

TODO: Handle unencoded DQUOTE embedded in cookie-purpose.

If the attribute-name case-insensitively matches the string "Purpose", the
user agent MUST process the cookie-av as follows:

1.  The cookie-purpose string consists of all the characters contained in
    the attribute-value.

2.  If the first and last characters of the cookie-purpose are not DQUOTE
    characters, ignore the cookie-av.

3.  If the first character of the cookie-purpose after the first DQUOTE
    character is not a VCHAR character, ignore the cookie-av.
    
4.  If cookie-purpose contains any non-SP or non-VCHAR characters, ignore
    the cookie-av.
    
5.  Append an attribute to the cookie-attribute-list with an
    attribute-name of "Purpose" and an attribute-value of cookie-purpose.

### The Exempt Attribute

If the attribute-name case-insensitively matches the string "Exempt", the
user agent MUST append an attribute to the cookie-attribute-list with an
attribute-name of Exempt and an empty attribute-value.

### The Third-Party Attribute

If the attribute-name case-insensitively matches the string "Third-Party",
the user agent MUST append an attribute to the cookie-attribute-list with
an attribute-name of Third-Party and an empty attribute-value.

### The Policy Attribute

If the attribute-name case-insensitively matches the string "Policy", the
user agent MUST process the cookie-av as follows:

TODO: Handle unencoded DQUOTE embedded in policy-value.
TODO: Determine how user agents should behave if cookie-policy contains
      a URI query or fragment.
TODO: Determine how user agents should behave if unable to locate or
      retrieve policy content.

If the attribute-name case-insensitively matches the string "Policy", the
user agent MUST process the cookie-av as follows:

1.  The cookie-policy string consists of all the characters contained in
    the attribute-value.

2.  If the first and last characters of the cookie-policy are not DQUOTE
    characters, ignore the cookie-av.

3.  If the characters between the first and last characters of the
    cookie-policy do not constitute a valid http-URL or https-URI, ignore
    the cookie-av.
    
4.  Append an attribute to the cookie-attribute-list with an
    attribute-name of "Policy" and an attribute-value of cookie-policy.

### The Consent Attribute

TODO: Handle empty cookie-consent value.
TODO: Clarify that servers should keep a record of consent, even if
      subsequently revoked, as servers are required to be able to
      prove consent was obtained.

If the attribute-name case-insensitively matches the string "Consent", the
user agent MUST process the cookie-av as follows:

1.  The cookie-consent string consists of all the characters contained in
    the attribute-value.
    
2.  If the cookie-policy does not constitute a valid IMF-fixdate, ignore
    the cookie-av.
    
3.  Append an attribute to the cookie-attribute-list with an
    attribute-name of "Consent" and an attribute-value of cookie-consent.

#### "Strict" and "Lax" enforcement {#strict-lax}

Same-site cookies in "Strict" enforcement mode will not be sent along with
top-level navigations which are triggered from a cross-site document context.
As discussed in {{top-level-navigations}}, this might or might not be compatible
with existing session management systems. In the interests of providing a
drop-in mechanism that mitigates the risk of CSRF attacks, developers may set
the `SameSite` attribute in a "Lax" enforcement mode that carves out an
exception which sends same-site cookies along with cross-site requests if and
only if they are top-level navigations which use a "safe" (in the {{RFC7231}}
sense) HTTP method.

Lax enforcement provides reasonable defense in depth against CSRF attacks that
rely on unsafe HTTP methods (like `POST`), but does not offer a robust defense
against CSRF as a general category of attack:

1. Attackers can still pop up new windows or trigger top-level navigations in
   order to create a "same-site" request (as described in section 2.1), which is
   only a speedbump along the road to exploitation.

2. Features like `<link rel='prerender'>` {{prerendering}} can be exploited
   to create "same-site" requests without the risk of user detection.

When possible, developers should use a session management mechanism such as
that described in {{top-level-navigations}} to mitigate the risk of CSRF more
completely.

## Storage Model {#storage-model}

TODO: Update with EU Cookie Law mechanisms.

The user agent stores the following fields about each cookie: name, value,
expiry-time, domain, path, creation-time, last-access-time,
persistent-flag, host-only-flag, secure-only-flag, http-only-flag,
and same-site-flag.

When the user agent "receives a cookie" from a request-uri with name
cookie-name, value cookie-value, and attributes cookie-attribute-list, the
user agent MUST process the cookie as follows:

1.  A user agent MAY ignore a received cookie in its entirety. For example, the
    user agent might wish to block receiving cookies from "third-party"
    responses or the user agent might not wish to store cookies that exceed some
    size.

2.  Create a new cookie with name cookie-name, value cookie-value. Set the
    creation-time and the last-access-time to the current date and time.

3.  If the cookie-attribute-list contains an attribute with an attribute-name
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

4.  If the cookie-attribute-list contains an attribute with an
    attribute-name of "Domain":

    1.  Let the domain-attribute be the attribute-value of the last
        attribute in the cookie-attribute-list with an attribute-name of
        "Domain".

    Otherwise:

    1.  Let the domain-attribute be the empty string.

5.  If the user agent is configured to reject "public suffixes" and the
    domain-attribute is a public suffix:

    1.  If the domain-attribute is identical to the canonicalized
        request-host:

        1.  Let the domain-attribute be the empty string.

        Otherwise:

        1.  Ignore the cookie entirely and abort these steps.

    NOTE: A "public suffix" is a domain that is controlled by a public registry,
    such as "com", "co.uk", and "pvt.k12.wy.us". This step is essential for
    preventing attacker.com from disrupting the integrity of example.com by
    setting a cookie with a Domain attribute of "com". Unfortunately, the set
    of public suffixes (also known as "registry controlled domains") changes
    over time. If feasible, user agents SHOULD use an up-to-date public suffix
    list, such as the one maintained by the Mozilla project at
    <http://publicsuffix.org/>.

6.  If the domain-attribute is non-empty:

    1.  If the canonicalized request-host does not domain-match the
        domain-attribute:

        1.  Ignore the cookie entirely and abort these steps.

        Otherwise:

        1.  Set the cookie's host-only-flag to false.

        2.  Set the cookie's domain to the domain-attribute.

    Otherwise:

    1.  Set the cookie's host-only-flag to true.

    2.  Set the cookie's domain to the canonicalized request-host.

7.  If the cookie-attribute-list contains an attribute with an
    attribute-name of "Path", set the cookie's path to attribute-value of
    the last attribute in the cookie-attribute-list with an attribute-name
    of "Path". Otherwise, set the cookie's path to the default-path of the
    request-uri.

8.  If the cookie-attribute-list contains an attribute with an
    attribute-name of "Secure", set the cookie's secure-only-flag to true.
    Otherwise, set the cookie's secure-only-flag to false.

9.  If the scheme component of the request-uri does not denote a "secure"
    protocol (as defined by the user agent), and the cookie's secure-only-flag
    is true, then abort these steps and ignore the cookie entirely.

10. If the cookie-attribute-list contains an attribute with an
    attribute-name of "HttpOnly", set the cookie's http-only-flag to true.
    Otherwise, set the cookie's http-only-flag to false.

11. If the cookie was received from a "non-HTTP" API and the cookie's
    http-only-flag is true, abort these steps and ignore the cookie entirely.

12. If the cookie's secure-only-flag is not set, and the scheme component of
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

13. If the cookie-attribute-list contains an attribute with an
    attribute-name of "SameSite", set the cookie's same-site-flag to
    attribute-value (i.e. either "Strict", "Lax", or "None"). Otherwise, set the
    cookie's same-site-flag to "None".

14. If the cookie's `same-site-flag` is not "None":

    1.  If the cookie was received from a "non-HTTP" API, and the API was called
        from a context whose "site for cookies" is not an exact match for
        request-uri's host's registered domain, then abort these steps and
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

15. If the cookie-name begins with a case-sensitive match for the string
    "__Secure-", abort these steps and ignore the cookie entirely unless the
    cookie's secure-only-flag is true.

16. If the cookie-name begins with a case-sensitive match for the string
    "__Host-", abort these steps and ignore the cookie entirely unless the
    cookie meets all the following criteria:

    1.  The cookie's secure-only-flag is true.

    2.  The cookie's host-only-flag is true.

    3.  The cookie-attribute-list contains an attribute with an attribute-name
        of "Path", and the cookie's path is `/`.

17. If the cookie store contains a cookie with the same name, domain,
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

18. Insert the newly-created cookie into the cookie store.

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

2.  Cookies whose secure-only-flag is not set, and which share a domain field
    with more than a predetermined number of other cookies.

3.  Cookies that share a domain field with more than a predetermined number of
    other cookies.

4.  All cookies.

If two cookies have the same removal priority, the user agent MUST evict the
cookie with the earliest last-access date first.

When "the current session is over" (as defined by the user agent), the user
agent MUST remove from the cookie store all cookies with the persistent-flag
set to false.

## The Cookie Header {#cookie}

The user agent includes stored cookies in the Cookie HTTP request header.

When the user agent generates an HTTP request, the user agent MUST NOT attach
more than one Cookie header field.

A user agent MAY omit the Cookie header in its entirety.  For example, the
user agent might wish to block sending cookies during "third-party" requests
from setting cookies (see {{third-party-cookies}}).

If the user agent does attach a Cookie header field to an HTTP request, the
user agent MUST send the cookie-string (defined below) as the value of the
header field.

The user agent MUST use an algorithm equivalent to the following algorithm to
compute the cookie-string from a cookie store and a request-uri:

1.  Let cookie-list be the set of cookies from the cookie store that meets all
    of the following requirements:

    *   Either:

        *   The cookie's host-only-flag is true and the canonicalized
            request-host is identical to the cookie's domain.

        Or:

        *   The cookie's host-only-flag is false and the canonicalized
            request-host domain-matches the cookie's domain.

    *   The request-uri's path path-matches the cookie's path.

    *  If the cookie's secure-only-flag is true, then the request-uri's
       scheme must denote a "secure" protocol (as defined by the user agent).

       NOTE: The notion of a "secure" protocol is not defined by this document.
       Typically, user agents consider a protocol secure if the protocol makes
       use of transport-layer security, such as SSL or TLS. For example, most
       user agents consider "https" to be a scheme that denotes a secure
       protocol.

    *  If the cookie's http-only-flag is true, then exclude the cookie if the
       cookie-string is being generated for a "non-HTTP" API (as defined by
       the user agent).

    *  If the cookie's same-site-flag is not "None", and the HTTP request is
       cross-site (as defined in {{same-site-requests}}) then exclude the
       cookie unless all of the following statements hold:

        1.  The same-site-flag is "Lax"

        2.  The HTTP request's method is "safe".

        3.  The HTTP request's target browsing context is a top-level browsing
            context.

2.  The user agent SHOULD sort the cookie-list in the following order:

    *  Cookies with longer paths are listed before cookies with shorter
       paths.

    *  Among cookies that have equal-length path fields, cookies with earlier
       creation-times are listed before cookies with later creation-times.

    NOTE: Not all user agents sort the cookie-list in this order, but this order
    reflects common practice when this document was written, and, historically,
    there have been servers that (erroneously) depended on this order.

3.  Update the last-access-time of each cookie in the cookie-list to the
    current date and time.

4.  Serialize the cookie-list into a cookie-string by processing each cookie
    in the cookie-list in order:

    1.  Output the cookie's name, the %x3D ("=") character, and the cookie's
        value.

    2.  If there is an unprocessed cookie in the cookie-list, output the
        characters %x3B and %x20 ("; ").

NOTE: Despite its name, the cookie-string is actually a sequence of octets, not
a sequence of characters.  To convert the cookie-string (or components
thereof) into a sequence of characters (e.g., for presentation to the user),
the user agent might wish to try using the UTF-8 character encoding {{RFC3629}}
to decode the octet sequence. This decoding might fail, however, because not
every sequence of octets is valid UTF-8.

# Implementation Considerations

## Limits

Practical user agent implementations have limits on the number and size of
cookies that they can store. General-use user agents SHOULD provide each of the
following minimum capabilities:

*   At least 4096 bytes per cookie (as measured by the sum of the length of the
    cookie's name, value, and attributes).

*   At least 50 cookies per domain.

*   At least 3000 cookies total.

Servers SHOULD use as few and as small cookies as possible to avoid reaching
these implementation limits and to minimize network bandwidth due to the
Cookie header being included in every request.

Servers SHOULD gracefully degrade if the user agent fails to return one or more
cookies in the Cookie header because the user agent might evict any cookie at
any time on orders from the user.

## Application Programming Interfaces

One reason the Cookie and Set-Cookie headers use such esoteric syntax is
that many platforms (both in servers and user agents) provide a string-based
application programming interface (API) to cookies, requiring
application-layer programmers to generate and parse the syntax used by the
Cookie and Set-Cookie headers, which many programmers have done incorrectly,
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

Cookies are often criticized for letting servers track users. For example, a
number of "web analytics" companies use cookies to recognize when a user returns
to a web site or visits another web site. Although cookies are not the only
mechanism servers can use to track users across HTTP requests, cookies
facilitate tracking because they are persistent across user agent sessions and
can be shared between hosts.

## Third-Party Cookies {#third-party-cookies}

Particularly worrisome are so-called "third-party" cookies. In rendering an HTML
document, a user agent often requests resources from other servers (such as
advertising networks). These third-party servers can use cookies to track the
user even if the user never visits the server directly. For example, if a user
visits a site that contains content from a third party and then later visits
another site that contains content from the same third party, the third party
can track the user between the two sites.

Given this risk to user privacy, some user agents restrict how third-party
cookies behave, and those restrictions vary widly. For instance, user agents
might block third-party cookies entirely by refusing to send Cookie headers or
process Set-Cookie headers during third-party requests. They might take a less
draconian approach by partitioning cookies based on the first-party context,
sending one set of cookies to a given third party in one first-party context,
and another to the same third party in another.

This document grants user agents wide latitude to experiment with third-party
cookie policies that balance the privacy and compatibility needs of their users.
However, this document does not endorse any particular third-party cookie
policy.

Third-party cookie blocking policies are often ineffective at achieving their
privacy goals if servers attempt to work around their restrictions to track
users. In particular, two collaborating servers can often track users without
using cookies at all by injecting identifying information into dynamic URLs.

## User Controls

TODO: Update to indicate user agents should allow users to revoke consent.

User agents SHOULD provide users with a mechanism for managing the cookies
stored in the cookie store. For example, a user agent might let users delete
all cookies received during a specified time period or all the cookies related
to a particular domain. In addition, many user agents include a user interface
element that lets users examine the cookies stored in their cookie store.

User agents SHOULD provide users with a mechanism for disabling cookies. When
cookies are disabled, the user agent MUST NOT include a Cookie header in
outbound HTTP requests and the user agent MUST NOT process Set-Cookie headers
in inbound HTTP responses.

Some user agents provide users the option of preventing persistent storage of
cookies across sessions. When configured thusly, user agents MUST treat all
received cookies as if the persistent-flag were set to false. Some popular
user agents expose this functionality via "private browsing" mode
{{Aggarwal2010}}.

TODO: Update to indicate user agents should allow consent to be provided
      per category, per domain, individually, or any combination thereof,
      either at the time of cookie receipt, or in advance via settings or
      other means.

Some user agents provide users with the ability to approve individual writes to
the cookie store. In many common usage scenarios, these controls generate a
large number of prompts. However, some privacy-conscious users find these
controls useful nonetheless.

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
and Set-Cookie headers is transmitted in the clear.

1.  All sensitive information conveyed in these headers is exposed to an
    eavesdropper.

2.  A malicious intermediary could alter the headers as they travel in either
    direction, with unpredictable results.

3.  A malicious client could alter the Cookie header before transmission,
    with unpredictable results.

Servers SHOULD encrypt and sign the contents of cookies (using whatever format
the server desires) when transmitting them to the user agent (even when sending
the cookies over a secure channel). However, encrypting and signing cookie
contents does not prevent an attacker from transplanting a cookie from one user
agent to another or from replaying the cookie at a later time.

In addition to encrypting and signing the contents of every cookie, servers that
require a higher level of security SHOULD use the Cookie and Set-Cookie
headers only over a secure channel. When using cookies over a secure channel,
servers SHOULD set the Secure attribute (see {{sane-secure}}) for every
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
subdomains). For example, consider foo.example.com and bar.example.com. The
foo.example.com server can set a cookie with a Domain attribute of
"example.com" (possibly overwriting an existing "example.com" cookie set by
bar.example.com), and the user agent will include that cookie in HTTP requests
to bar.example.com. In the worst case, bar.example.com will be unable to
distinguish this cookie from a cookie it set itself. The foo.example.com
server might be able to leverage this ability to mount an attack against
bar.example.com.

Even though the Set-Cookie header supports the Path attribute, the Path
attribute does not provide any integrity protection because the user agent
will accept an arbitrary Path attribute in a Set-Cookie header. For
example, an HTTP response to a request for http://example.com/foo/bar can set
a cookie with a Path attribute of "/qux". Consequently, servers SHOULD NOT
both run mutually distrusting services on different paths of the same host and
use cookies to store security-sensitive information.

An active network attacker can also inject cookies into the Cookie header
sent to https://example.com/ by impersonating a response from
http://example.com/ and injecting a Set-Cookie header. The HTTPS server
at example.com will be unable to distinguish these cookies from cookies that
it set itself in an HTTPS response. An active network attacker might be able
to leverage this ability to mount an attack against example.com even if
example.com uses HTTPS exclusively.

Servers can partially mitigate these attacks by encrypting and signing the
contents of their cookies. However, using cryptography does not mitigate the
issue completely because an attacker can replay a cookie he or she received from
the authentic example.com server in the user's session, with unpredictable
results.

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
webmail provider `https://example.com/`. They might expect that clicking on an
emailed link to `https://projects.com/secret/project` would show them the secret
project that they're authorized to see, but if `projects.com` has marked their
session cookies as `SameSite`, then this cross-site navigation won't send them
along with the request. `projects.com` will render a 404 error to avoid leaking
secret information, and the user will be quite confused.

Developers can avoid this confusion by adopting a session management system that
relies on not one, but two cookies: one conceptually granting "read" access,
another granting "write" access. The latter could be marked as `SameSite`, and
its absence would prompt a reauthentication step before executing any
non-idempotent action. The former could drop the `SameSite` attribute entirely,
or choose the "Lax" version of enforcement, in order to allow users access to
data via top-level navigation.

### Mashups and Widgets

The `SameSite` attribute is inappropriate for some important use-cases. In
particular, note that content intended for embedding in a cross-site contexts
(social networking widgets or commenting services, for instance) will not have
access to same-site cookies. Cookies may be required for requests triggered in
these cross-site contexts in order to provide seamless functionality that relies
on a user's state.

Likewise, some forms of Single-Sign-On might require cookie-based authentication
in a cross-site context; these mechanisms will not function as intended with
same-site cookies.

### Server-controlled

SameSite cookies in and of themselves don't do anything to address the
general privacy concerns outlined in Section 7.1 of {{RFC6265}}. The "SameSite"
attribute is set by the server, and serves to mitigate the risk of certain kinds
of attacks that the server is worried about. The user is not involved in this
decision. Moreover, a number of side-channels exist which could allow a server
to link distinct requests even in the absence of cookies. Connection and/or
socket pooling, Token Binding, and Channel ID all offer explicit methods of
identification that servers could take advantage of.

# IANA Considerations

The permanent message header field registry (see {{RFC3864}}) needs to be
updated with the following registrations.

## Cookie {#iana-cookie}

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

# Acknowledgements
{:numbered="false"}
This document is a minor update of RFC 6265, adding small features, and
aligning the specification with the reality of today's deployments. Here,
we're standing upon the shoulders of giants.
