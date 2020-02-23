---
title: Using TLS 1.3 with HTTP/2
docname: draft-ietf-httpbis-http2-tls13-latest
category: std
updates: 7540

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP

pi: [toc, sortrefs, symrefs]
stand_alone: yes

author:
 -
       ins: D. Benjamin
       name: David Benjamin
       organization: Google LLC
       email: davidben@google.com

normative:
  RFC2119:
  RFC5246:
  RFC7230:
  RFC7301:
  RFC7540:
  RFC8446:

informative:
  RFC8470:


--- abstract

This document updates RFC 7540 by forbidding TLS 1.3 post-handshake
authentication, as an analog to the existing TLS 1.2 renegotiation restriction.

--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <https://httpwg.org/>; source
code and issues list for this draft can be found at
<https://github.com/httpwg/http-extensions/labels/http2-tls13>.

--- middle

# Introduction

TLS 1.2 {{RFC5246}} and earlier versions of TLS support renegotiation, a
mechanism for changing
parameters and keys partway through a connection. This was sometimes used to
implement reactive client authentication in HTTP/1.1 {{RFC7230}}, where the
server decides whether or not to request a client certificate based on the HTTP
request.

HTTP/2 {{RFC7540}} multiplexes multiple HTTP requests over a single connection,
which is incompatible with the mechanism above. Clients cannot correlate the
certificate request with the HTTP request that triggered it. Thus, Section
9.2.1 of {{RFC7540}} forbids renegotiation.

TLS 1.3 {{RFC8446}} removes renegotiation and replaces it with separate
post-handshake authentication and key update mechanisms. Post-handshake
authentication has the same problems with multiplexed protocols as TLS 1.2
renegotiation, but the prohibition in {{RFC7540}}
only applies to renegotiation.

This document updates HTTP/2 {{RFC7540}} to similarly forbid TLS 1.3 post-handshake
authentication.


# Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 {{RFC2119}} {{!RFC8174}}
when, and only when, they appear in all capitals, as shown here.


# Post-Handshake Authentication in HTTP/2

HTTP/2 servers MUST NOT send post-handshake TLS 1.3 CertificateRequest messages.
HTTP/2 clients MUST treat such messages as connection errors (see Section 5.4.1
of {{RFC7540}}) of type PROTOCOL\_ERROR.

{{RFC7540}} permitted renegotiation before the HTTP/2 connection preface to
provide confidentiality of the client certificate. TLS 1.3 encrypts the client
certificate in the initial handshake, so this is no longer necessary. HTTP/2
servers MUST NOT send post-handshake TLS 1.3 CertificateRequest messages before
the connection preface.

The above applies even if the client offered the `post_handshake_auth` TLS
extension. This extension is advertised independently of the selected
Application-Layer Protocol Negotiation (ALPN)
protocol {{RFC7301}}, so it is not sufficient to resolve the conflict with
HTTP/2. HTTP/2 clients that also offer other ALPN protocols, notably HTTP/1.1,
in a TLS ClientHello MAY include the `post_handshake_auth` extension to support
those other protocols. This does not indicate support in HTTP/2.


# Other Post-Handshake TLS Messages in HTTP/2

{{RFC8446}} defines two other messages that are exchanged after the handshake is
complete: KeyUpdate and NewSessionTicket.

KeyUpdate messages only affect TLS itself and do not require any interaction
with the application protocol. HTTP/2 implementations MUST support key updates
when TLS 1.3 is negotiated.

NewSessionTicket messages are also permitted. Though these interact with HTTP
when early data is enabled, these interactions are defined in {{RFC8470}} and
are allowed for in the design of HTTP/2.

Unless the use of a new type of TLS message depends on an interaction with the
application-layer protocol, that TLS message can be sent after the handshake
completes.


# Security Considerations

This document resolves a compatibility concern between HTTP/2 and TLS 1.3 when
supporting post-handshake authentication with HTTP/1.1. This lowers the barrier
for deploying TLS 1.3, a major security improvement over TLS 1.2.


# IANA Considerations

This document has no IANA actions.

--- back
