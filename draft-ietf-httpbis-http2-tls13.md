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


--- abstract

This document clarifies the use of TLS 1.3 post-handshake authentication and
key update with HTTP/2.

--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <https://httpwg.org/>; source
code and issues list for this draft can be found at
<https://github.com/httpwg/http-extensions/labels/http2-tls13>.

--- middle

# Introduction

TLS 1.2 {{RFC5246}} and earlier support renegotiation, a mechanism for changing
parameters and keys partway through a connection. This was sometimes used to
implement reactive client authentication in HTTP/1.1 {{RFC7230}}, where the
server decides whether to request a client certificate based on the HTTP
request.

HTTP/2 {{RFC7540}} multiplexes multiple HTTP requests over a single connection,
which is incompatible with the mechanism above. Clients cannot correlate the
certificate request with the HTTP request which triggered it. Thus, section
9.2.1 of {{RFC7540}} forbids renegotiation.

TLS 1.3 {{RFC8446}} updates TLS 1.2 to remove renegotiation in favor of
separate post-handshake authentication and key update mechanisms. The former
shares the same problems with multiplexed protocols, but has a different name.
This makes it ambiguous whether post-handshake authentication is allowed in TLS
1.3.

This document clarifies that the prohibition applies to post-handshake
authentication but not to key updates.


# Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 {{RFC2119}} {{!RFC8174}}
when, and only when, they appear in all capitals, as shown here.


# Post-Handshake Authentication in HTTP/2

The prohibition on renegotiation in section 9.2.1 of {{RFC7540}} additionally
applies to TLS 1.3 post-handshake authentication.  HTTP/2 servers MUST NOT send
post-handshake TLS 1.3 CertificateRequest messages. HTTP/2 clients MUST treat
TLS 1.3 post-handshake authentication as a connection error (see section 5.4.1
of {{RFC7540}}) of type PROTOCOL\_ERROR.

{{RFC7540}} permitted renegotiation before the HTTP/2 connection preface to
provide confidentiality of the client certificate. TLS 1.3 encrypts the client
certificate in the initial handshake, so this is no longer necessary. HTTP/2
servers MUST NOT send post-handshake TLS 1.3 CertificateRequest messages before
the connection preface.

The above applies even if the client offered the `post_handshake_auth` TLS
extension. This extension is advertised independently of the selected ALPN
protocol {{RFC7301}}, so it is not sufficient to resolve the conflict with
HTTP/2. HTTP/2 clients that also offer other ALPN protocols, notably HTTP/1.1,
in a TLS ClientHello MAY include the `post_handshake_auth` extension to support
those other protocols. This does not indicate support in HTTP/2.


# Key Updates in HTTP/2

Section 9.2.1 of {{RFC7540}} does not extend to TLS 1.3 KeyUpdate messages.
HTTP/2 implementations MUST support key updates when TLS 1.3 is negotiated.


# Security Considerations

This document clarifies how to use HTTP/2 with TLS 1.3 and resolves a
compatibility concern when supporting post-handshake authentication with
HTTP/1.1. This lowers the barrier for deploying TLS 1.3, a major security
improvement over TLS 1.2. Permitting key updates allows key material to be
refreshed in long-lived HTTP/2 connections.


# IANA Considerations

This document has no IANA actions.

--- back
