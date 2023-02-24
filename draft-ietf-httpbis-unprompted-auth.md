---
title: HTTP Unprompted Authentication
docname: draft-schinazi-httpbis-unprompted-auth-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
category: std
wg: HTTPBIS
area: "Applications and Real-Time"
venue:
  group: "HTTP"
  type: "Working Group"
  mail: "ietf-http-wg@w3.org"
  arch: "https://lists.w3.org/Archives/Public/ietf-http-wg/"
  github: "DavidSchinazi/draft-schinazi-httpbis-transport-auth"
  latest: "https://DavidSchinazi.github.io/draft-schinazi-httpbis-transport-auth/draft-schinazi-httpbis-unprompted-auth.html"
keyword:
  - secure
  - tunnels
  - masque
  - http-ng
author:
  -
    ins: D. Schinazi
    name: David Schinazi
    org: Google LLC
    street: 1600 Amphitheatre Parkway
    city: Mountain View
    region: CA
    code: 94043
    country: United States of America
    email: dschinazi.ietf@gmail.com
  -
    ins: D. Oliver
    name: David M. Oliver
    org: Guardian Project
    email: david@guardianproject.info
    uri: https://guardianproject.info
  -
    ins: J. Hoyland
    name: Jonathan Hoyland
    org: Cloudflare Inc.
    email: jonathan.hoyland@gmail.com

informative:
  H2:
    =: RFC9113
    display: HTTP/2
  H3:
    =: RFC9114
    display: HTTP/3

--- abstract

Existing HTTP authentication mechanisms are probeable in the sense that it is
possible for an unauthenticated client to probe whether an origin serves
resources that require authentication. It is possible for an origin to hide the
fact that it requires authentication by not generating Unauthorized status
codes, however that only works with non-cryptographic authentication schemes:
cryptographic schemes (such as signatures or message authentication codes)
require a fresh nonce to be signed, and there is no existing way for the origin
to share such a nonce without exposing the fact that it serves resources that
require authentication. This document proposes a new non-probeable cryptographic
authentication scheme.

--- middle

# Introduction {#introduction}

Existing HTTP authentication mechanisms (see {{Section 11 of !HTTP=RFC9110}})
are probeable in the sense that it is possible for an unauthenticated client to
probe whether an origin serves resources that require authentication. It is
possible for an origin to hide the fact that it requires authentication by not
generating Unauthorized status codes, however that only works with
non-cryptographic authentication schemes: cryptographic schemes (such as
signatures or message authentication codes) require a fresh nonce to be signed,
and there is no existing way for the origin to share such a nonce without
exposing the fact that it serves resources that require authentication. This
document proposes a new non-probeable cryptographic authentication scheme.

There are scenarios where servers may want to expose the fact that
authentication is required for access to specific resources. This is left for
future work.

## Conventions and Definitions {#conventions}

{::boilerplate bcp14-tagged}

This document uses the following terminology from {{Section 3 of
!STRUCTURED-FIELDS=RFC8941}} to specify syntax and parsing: Integer and Byte
Sequence.

# Computing the Authentication Proof {#compute-proof}

This document only defines the Signature and HMAC authentication schemes for
uses of HTTP with TLS {{!TLS=RFC8446}}. This includes any use of HTTP over TLS
as typically used for HTTP/2 {{H2}}, or HTTP/3 {{H3}} where the transport
protocol uses TLS as its authentication and key exchange mechanism
{{?QUIC-TLS=RFC9001}}.

The user agent leverages a TLS keying material exporter {{!KEY-EXPORT=RFC5705}}
to generate a nonce which can be signed using the user's key. The keying
material exporter uses a label that starts with the characters
"EXPORTER-HTTP-Unprompted-Authentication-" (see {{schemes}} for the labels and
contexts used by each scheme). The TLS keying material exporter is used to
generate a 32-byte key which is then used as a nonce.

# Header Field Definition {#header-definition}

The "Unprompted-Authentication" header field allows a user agent to authenticate
with an origin server. The authentication is scoped to the HTTP request
associated with this header field. The value of the Unprompted-Authentication
header field is a credentials object, as defined in {{Section 11.4 of HTTP}}.
Credentials contain an authentication scheme followed by optional authentication
parameters.

# Authentication Parameters

This specification defines the following authentication parameters, they can be
used by the authentication schemes defined in {{schemes}}.

## The u Parameter {#parameter-u}

The OPTIONAL "u" (user ID) parameter is a byte sequence that specifies the user
ID that the user agent wishes to authenticate.

## The p Parameter {#parameter-p}

The OPTIONAL "p" (proof) parameter is a byte sequence that specifies the proof
that the user agent provides to attest to possessing the credential that matches
its user ID.

## The s Parameter {#parameter-s}

The OPTIONAL "s" (signature) parameter is an integer that specifies the
signature algorithm used to compute the proof transmitted in the "p" directive.
Its value is an integer between 0 and 255 inclusive from the IANA "TLS
SignatureAlgorithm" registry maintained at
<[](https://www.iana.org/assignments/tls-parameters#tls-parameters-16)>.

## The h Parameter {#parameter-h}

The OPTIONAL "h" (hash) parameter is an integer that specifies the hash
algorithm used to compute the proof transmitted in the "p" directive. Its value
is an integer between 0 and 255 inclusive from the IANA "TLS HashAlgorithm"
registry maintained at
<[](https://www.iana.org/assignments/tls-parameters#tls-parameters-18)>.

# Authentication Schemes {#schemes}

This document defines the "Signature" and "HMAC" HTTP authentication schemes.

## Signature {#signature}

The "Signature" HTTP Authentication Scheme uses asymmetric cyptography.
User agents possess a user ID and a public/private key pair, and origin servers
maintain a mapping of authorized user IDs to their associated public keys. When
using this scheme, the "u", "p", and "s" parameters are REQUIRED. The TLS keying
material export label for this scheme is
"EXPORTER-HTTP-Unprompted-Authentication-Signature" and the associated context
is empty. The nonce is then signed using the selected asymmetric signature
algorithm and transmitted as the proof directive.

For example, the user ID "john.doe" authenticating using Ed25519
{{?ED25519=RFC8410}} could produce the following header field (lines are folded
to fit):

~~~
Unprompted-Authentication: Signature u=:am9obi5kb2U=:;s=7;
p=:SW5zZXJ0IHNpZ25hdHVyZSBvZiBub25jZSBoZXJlIHdo
aWNoIHRha2VzIDUxMiBiaXRzIGZvciBFZDI1NTE5IQ==:
~~~

## HMAC {#hmac}

The "HMAC" HTTP Authentication Scheme uses symmetric cyptography. User
agents possess a user ID and a secret key, and origin servers maintain a mapping
of authorized user IDs to their associated secret key. When using this scheme,
the "u", "p", and "h" parameters are REQUIRED. The TLS keying material export
label for this scheme is "EXPORTER-HTTP-Unprompted-Authentication-HMAC" and the
associated context is empty. The nonce is then HMACed using the selected HMAC
algorithm and transmitted as the proof directive.

For example, the user ID "john.doe" authenticating using HMAC-SHA-512
{{?SHA=RFC6234}} could produce the following header field (lines are folded to
fit):

~~~
Unprompted-Authentication: HMAC u="am9obi5kb2U=";h=6;
p="SW5zZXJ0IEhNQUMgb2Ygbm9uY2UgaGVyZSB3aGljaCB0YWtl
cyA1MTIgYml0cyBmb3IgU0hBLTUxMiEhISEhIQ=="
~~~

## Other HTTP Authentication Schemes

The HTTP Authentication Scheme registry maintained by IANA at
<[](https://www.iana.org/assignments/http-authschemes/http-authschemes.xhtml)>
contains entries not defined in this document. Those entries MAY be used with
Unprompted Authentication.

# Intermediary Considerations {#intermediary}

Since the Signature and HMAC HTTP Authentication Schemes leverage TLS keying
material exporters, their output
cannot be transparently forwarded by HTTP intermediaries. HTTP intermediaries
that support this specification will validate the authentication received from
the client themselves, then inform the upstream HTTP server of the presence of
valid authentication using some other mechanism.

# Security Considerations {#security}

Unprompted Authentication allows a user-agent to authenticate to an origin
server while guaranteeing freshness and without the need for the server
to transmit a nonce to the user agent. This allows the server to accept
authenticated clients without revealing that it supports or expects
authentication for some resources. It also allows authentication without
the user agent leaking the presence of authentication to observers due to
clear-text TLS Client Hello extensions.

The authentication proofs described in this document are not bound to individual
HTTP requests; if the same user sends an authentication proof on multiple
requests they will all be identical. This allows for better compression when
sending over the wire, but implies that client implementations that multiplex
different security contexts over a single HTTP connection need to ensure that
those contexts cannot read each other's header fields. Otherwise, one context
would be able to replay the unprompted authentication header field of another.
This constraint is met by modern Web browsers. If an attacker were to compromise
the browser such that it could access another context's memory, the attacker
might also be able to access the corresponding key, so binding authentication to
requests would not provide much benefit in practice.

# IANA Considerations {#iana}

## Unprompted-Authentication Header Field {#iana-header}

This document will request IANA to register the following entry in the "HTTP
Field Name" registry maintained at
<[](https://www.iana.org/assignments/http-fields)>:

Field Name:

: Unprompted-Authentication

Template:

: None

Status:

: provisional (permanent if this document is approved)

Reference:

: This document

Comments:

: None
{: spacing="compact"}

## HTTP Authentication Schemes Registry {#iana-schemes}

This document, if approved, requests IANA to add two new entries to the
"HTTP Authentication Schemes" Registry maintained at
<[](https://www.iana.org/assignments/http-authschemes)>.
Both entries have the Reference set to this document, and the Notes empty.
The Authentication Scheme Name of the entries are:

* Signature

* HMAC

## TLS Keying Material Exporter Labels {#iana-exporter-label}

This document, if approved, requests IANA to register the following entries in
the "TLS Exporter Labels" registry maintained at
<[](https://www.iana.org/assignments/tls-parameters#exporter-labels)>:

* EXPORTER-HTTP-Unprompted-Authentication-Signature

* EXPORTER-HTTP-Unprompted-Authentication-HMAC

Both of these entries are listed with the following qualifiers:

DTLS-OK:

: N

Recommended:

: Y

Reference:

: This document
{: spacing="compact"}

--- back

# Acknowledgments {#acknowledgments}
{:numbered="false"}

The authors would like to thank many members of the IETF community, as this
document is the fruit of many hallway conversations. Ben Schwartz contributed
ideas to this document.

