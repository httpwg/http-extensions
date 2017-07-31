---
title: The ORIGIN HTTP/2 Frame
abbrev: ORIGIN Frames
docname: draft-ietf-httpbis-origin-frame-latest
date: 2017
category: std

ipr: trust200902
area: General
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
    ins: E. Nygren
    name: Erik Nygren
    organization: Akamai
    email: nygren@akamai.com

normative:
  RFC2119:

informative:


--- abstract

This document specifies the ORIGIN frame for HTTP/2, to indicate what origins are available on a
given connection.

--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/origin-frame>.

--- middle

# Introduction

HTTP/2 {{!RFC7540}} allows clients to coalesce different origins {{!RFC6454}} onto the same
connection when certain conditions are met. However, in certain cases, a connection is not
usable for a coalesced origin, so the 421 (Misdirected Request) status code ({{?RFC7540}}, Section
9.1.2) was defined.

Using a status code in this manner allows clients to recover from misdirected requests, but at the
penalty of adding latency. To address that, this specification defines a new HTTP/2 frame type,
"ORIGIN", to allow servers to indicate what origins a connection is usable for.

Additionally, experience has shown that HTTP/2's requirement to establish server authority using
both DNS and the server's certificate is onerous. This specification relaxes the requirement to
check DNS when the ORIGIN frame is in use. Doing so has additional benefits, such as removing the
latency associated with some DNS lookups.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
{{RFC2119}}.

# The ORIGIN HTTP/2 Frame

The ORIGIN HTTP/2 frame ({{!RFC7540}}, Section 4) allows a server to indicate what origin(s)
{{!RFC6454}} the server would like the client to consider as members of the Origin Set ({{set}})
for the connection it occurs within.

## Syntax {#syntax}

The ORIGIN frame type is 0xc (decimal 12), and contains zero to many Origin-Entry.

~~~~
+-------------------------------+-------------------------------+
|         Origin-Entry (*)                                    ...
+-------------------------------+-------------------------------+
~~~~

An Origin-Entry is a length-delimited string:

~~~~
+-------------------------------+-------------------------------+
|         Origin-Len (16)       | ASCII-Origin?               ...
+-------------------------------+-------------------------------+
~~~~

Specifically:

Origin-Len:
: An unsigned, 16-bit integer indicating the length, in octets, of the ASCII-Origin field.

Origin:
: An OPTIONAL sequence of characters containing the ASCII serialization of an origin ({{!RFC6454}}, Section 6.2) that the sender believes this connection is or could be authoritative for.

The ORIGIN frame does not define any flags. However, future updates to this specification MAY
define flags. See {{process}}.


## Processing ORIGIN Frames {#process}

The ORIGIN frame is a non-critical extension to HTTP/2. Endpoints that do not support this frame
can safely ignore it upon receipt.

When received by an implementing client, it is used to initialise and manipulate the Origin Set
(see {{set}}), thereby changing how the client establishes authority for origin servers (see
{{authority}}).

The origin frame MUST be sent on stream 0; an ORIGIN frame on any other stream is invalid and MUST
be ignored.

Likewise, the ORIGIN frame is only valid on connections with the "h2" protocol identifier, or when
specifically nominated by the protocol's definition; it MUST be ignored when received on a
connection with the "h2c" protocol identifier.

This specification does not define any flags for the ORIGIN frame, but future updates might use
them to change its semantics. The first four flags (0x1, 0x2, 0x4 and 0x8) are reserved for
backwards-incompatible changes, and therefore when any of them are set, the ORIGIN frame containing
them MUST be ignored by clients conforming to this specification, unless the flag's semantics are
understood. The remaining flags are reserved for backwards-compatible changes, and do not affect
processing by clients conformant to this specification.

The ORIGIN frame describes a property of the connection, and therefore is processed hop-by-hop. An
intermediary MUST NOT forward ORIGIN frames. Clients configured to use a proxy MUST ignore any
ORIGIN frames received from it.

Each ASCII-Origin field in the frame's payload MUST be parsed as an ASCII serialisation of an
origin ({{!RFC6454}}, Section 6.2). If parsing fails, the field MUST be ignored.

See {{algo}} for an illustrative algorithm for processing ORIGIN frames.


## The Origin Set {#set}

The set of origins (as per {{!RFC6454}}) that a given connection might be used for is known in this
specification as the Origin Set.

By default, a connections's Origin Set is uninitialised. When an ORIGIN frame is first received
and successfully processed by a client, the connection's Origin Set is defined to contain an
initial origin.  The initial origin is composed from:

  - Scheme: "https"
  - Host: the value sent in Server Name Indication (SNI, {{!RFC6066}} Section 3), converted to lower case
  - Port: the remote port of the connection (i.e., the server's port)

The contents of that ORIGIN frame (and subsequent ones) allows the server to incrementally add new
origins to the Origin Set, as described in {{process}}.

The Origin Set is also affected by the 421 (Misdirected Request) response status code, defined in
{{!RFC7540}} Section 9.1.2. Upon receipt of a response with this status code, implementing clients
MUST create the ASCII serialisation of the corresponding request's origin (as per {{!RFC6454}},
Section 6.2) and remove it from the connection's Origin Set, if present.

Note:

: When sending an ORIGIN frame to a connection that is initialised as an Alternative Service
  {{?RFC7838}}, the initial origin set {{set}} will contain an origin with the appropriate
  scheme and hostname (since Alternative Services specifies that the origin's hostname be sent
  in SNI). However, it is possible that the port will be different than that of the intended
  origin, since the initial origin set is calculated using the actual port in use, which can be
  different for the alternative service. In this case, the intended origin needs to be sent in
  the ORIGIN frame explicitly.

: For example, a client making requests for "https://example.com" is directed to an alternative
  service at ("h2", "x.example.net", "8443").  If this alternative service sends an ORIGIN
  frame, the initial origin will be "https://example.com:8443".  The client will not be able to
  use the alternative service to make requests for "https://example.com" unless that origin is
  explicitly included in the ORIGIN frame.


## Authority, Push and Coalescing with ORIGIN {#authority}

{{!RFC7540}}, Section 10.1 uses both DNS and the presented TLS certificate to establish the origin
server(s) that a connection is authoritative for, just as HTTP/1.1 does in {{?RFC7230}}.

Furthermore, {{!RFC7540}} Section 9.1.1 explicitly allows a connection to be used for more than one
origin server, if it is authoritative. This affects what requests can be sent on the connection,
both in HEADERS frame by the client and as PUSH_PROMISE frames from the server ({{!RFC7540}}, Section 8.2.2).

Once an Origin Set has been initialised for a connection, clients that implement this specification
use it to help determine what the connection is authoritative for. Specifically, such clients MUST
NOT consider a connection to be authoritative for an origin not present in the Origin Set, and
SHOULD use the connection for all requests to origins in the Origin Set for which the connection is
authoritative, unless there are operational reasons for opening a new connection.

Note that for a connection to be considered authoritative for a given origin, the client is still
required to obtain a certificate that passes suitable checks; see {{!RFC7540}}
Section 9.1.1 for more information. This includes verifying that the host matches a `dNSName` value
from the certificate `subjectAltName` field (using the wildcard rules defined in {{!RFC2818}}; see
also {{!RFC5280}} Section 4.2.1.6).

Additionally, clients MAY avoid consulting DNS to establish the connection's authority for new
requests.

Because ORIGIN can change the set of origins a connection is used for over time, it is possible
that a client might have more than one viable connection to an origin open at any time. When this
occurs, clients SHOULD not emit new requests on any connection whose Origin Set is a proper subset
of another connection's Origin Set, and SHOULD close it once all outstanding requests are satisfied.

The Origin Set is unaffected by any alternative services {{?RFC7838}} advertisements made by the
server.  Advertising an alternative service does not affect whether a server is authoritative.


# IANA Considerations

This specification adds an entry to the "HTTP/2 Frame Type" registry.

* Frame Type: ORIGIN
* Code: 0xc
* Specification: [this document]


# Security Considerations

Clients that blindly trust the ORIGIN frame's contents will be vulnerable to a large number of
attacks. See {{authority}} for mitigations.

Relaxing the requirement to consult DNS when determining authority for an origin means that an
attacker who possesses a valid certificate no longer needs to be on-path to redirect traffic to
them; instead of modifying DNS, they need only convince the user to visit another Web site, in
order to coalesce connections to the target onto their existing connection. Clients can mitigate
this attack in a variety of ways; examples include checking for a Signed Certificate Timestamp
{{?RFC6929}}, or performing certificate revocation checks.

The Origin Set's size is unbounded by this specification, and thus could be used by attackers to
exhaust client resources. To mitigate this risk, clients can monitor their state commitment and
close the connection if it is too high.
--- back


# Non-Normative Processing Algorithm {#algo}

The following algorithm illustrates how a client could handle received ORIGIN frames:

1. If the client is configured to use a proxy for the connection, ignore the frame and stop processing.
2. If the connection is not identified with the "h2" protocol identifier or another protocol that has explicitly opted into this specification, ignore the frame and stop processing.
3. If the frame occurs upon any stream except stream 0, ignore the frame and stop processing.
4. If any of the flags 0x1, 0x2, 0x4 or 0x8 are set, ignore the frame and stop processing.
5. If no previous ORIGIN frame on the connection has reached this step, initialise the Origin Set as per {{set}}.
6. For each `Origin-Entry` in the frame payload:
   1. Parse `ASCII-Origin` as an ASCII serialization of an origin ({{!RFC6454}}, Section 6.2) and let the result be `parsed_origin`. If parsing fails, skip to the next `Origin-Entry`.
   5. Add `parsed_origin` to the Origin Set.


# Operational Considerations for Servers {#server-ops}

The ORIGIN frame allows a server to indicate for which origins a given connection ought be used.
The set of origins advertised using this mechanism is under control of the server; servers are not
obligated to use it, or to advertise all origins which they might be able to answer a request for.

For example, it can be used to inform the client that the connection is to only be used for the
SNI-based origin, by sending an empty ORIGIN frame. Or, a larger number of origins can be indicated
by including a payload.

Generally, this information is most useful to send before sending any part of a response that might
initiate a new connection; for example, `Link` headers {{?RFC5988}} in a response HEADERS, or links
in the response body.

Therefore, the ORIGIN frame ought be sent as soon as possible on a connection, ideally before any
HEADERS or PUSH_PROMISE frames.

However, if it's desirable to associate a large number of origins with a connection, doing so might
introduce end-user perceived latency, due to their size. As a result, it might be necessary to
select a "core" set of origins to send initially, expanding the set of origins the connection is
used for with subsequent ORIGIN frames later (e.g., when the connection is idle).

That said, senders are encouraged to include as many origins as practical within a single ORIGIN
frame; clients need to make decisions about creating connections on the fly, and if the origin
set is split across many frames, their behaviour might be suboptimal.

Senders take note that, as per {{!RFC6454}} Section 4, the values in an ORIGIN header need to be
case-normalised before serialisation.

Finally, servers that host alternative services {{?RFC7838}} will need to explicitly advertise
their origins when sending ORIGIN, because the default contents of the Origin Set (as per {{set}})
do not contain any Alternative Services' origins, even if they have been used previously on the
connection.
