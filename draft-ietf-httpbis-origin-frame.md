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
    organization: Akamai
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
connection when certain conditions are met. However, in certain cases, a connection is is not
usable for a coalesced origin, so the 421 (Misdirected Request) status code ({{?RFC7540}}, Section
9.1.2) was defined.

Using a status code in this manner allows clients to recover from misdirected requests, but at the
penalty of adding latency. To address that, this specification defines a new HTTP/2 frame type,
"ORIGIN", to allow servers to indicate what origins a connection is usable for.

Additionally, experience has shown that HTTP/2's requirement to establish server authority using
both DNS and the server's certificate is onerous. This specification relaxes the requirement to
check DNS when the ORIGIN frame is in use.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
{{RFC2119}}.

# The ORIGIN HTTP/2 Frame

The ORIGIN HTTP/2 frame ({{!RFC7540}}, Section 4) allows a server to indicate what origin(s)
{{!RFC6454}} the server would like the client to consider as members of the Origin Set ({{set}})
for the connection it occurs within.

## Syntax {#syntax}

The ORIGIN frame type is 0xb (decimal 11).

~~~~
+-------------------------------+-------------------------------+
|         Origin-Len (16)       | ASCII-Origin? (*)           ...
+-------------------------------+-------------------------------+
~~~~

The ORIGIN frame's payload contains the following fields, sets of which may be repeated within the
frame to indicate multiple origins:

Origin-Len:
: An unsigned, 16-bit integer indicating the length, in octets, of the ASCII-Origin field.

Origin:
: An optional sequence of characters containing the ASCII serialization of an origin ({{!RFC6454}}, Section 6.2) that the sender believes this connection is or could be authoritative for.

The ORIGIN frame does not define any flags. However, future updates to this specification MAY
define flags. See {{process}}.


## Processing ORIGIN Frames {#process}

The ORIGIN frame is a non-critical extension to HTTP/2. Endpoints that do not support this frame
can safely ignore it upon receipt.

When received by an implementing client, it is used to manipulate the Origin Set (see {{set}}),
thereby changing how the client establishes authority for origin servers (see {{authority}}).

The origin frame MUST be sent on stream 0; an ORIGIN frame on any other stream is invalid and MUST
be ignored.

Likewise, the ORIGIN frame is only valid on connections with the "h2" protocol identifier, or when
specifically nominated by the protocol's definition; it MUST be ignored when received on a
connection with the "h2c" protocol identifier.

This specification does not define any flags for the ORIGIN frame, but future updates might use
them to change its semantics. The first four flags (0x1, 0x2, 0x4 and 0x8) are reserved for
backwards-incompatible changes, and therefore when any of them are set, the ORIGIN frame containing
them MUST be ignored by clients conforming to this specification. The remaining flags are reserved
for backwards-compatible changes, and do not affect processing by clients conformant to this
specification.

The ORIGIN frame is processed hop-by-hop. An intermediary MUST NOT forward ORIGIN frames. Clients
configured to use a proxy MUST ignore any ORIGIN frames received from it.

Each ASCII-Origin field in the frame's payload MUST be parsed as an ASCII serialisation of an
origin ({{!RFC6454}}, Section 6.2). If parsing fails, the field MUST be ignored.

Senders should note that, as per {{!RFC6454}} Section 4, the values in an ORIGIN header need to be
case-normalised before serialisation.

Once parsed, the value MUST have:

* a scheme of "https", 
* a host that is reflected in a `subjectAltName` of the connection's TLS certificate (using the wildcard rules defined in {{!RFC2818}}, Section 3.1), and 
* a port that reflects the connection's remote port on the client. 

If any of these requirements are violated, the client MUST ignore the field (but still continue
processing the frame).

See {{algo}} for an illustrative algorithm for processing ORIGIN frames.


## The Origin Set {#set}

The set of origins (as per {{!RFC6454}}) that a given connection might be used for is known in this
specification as the Origin Set.

When an ORIGIN frame is first received by a client, the connection's Origin Set is defined to
contain a single origin, composed from:

  - Scheme: "https"
  - Host: the value sent in Server Name Indication ({{!RFC6066}} Section 3), converted to lower case
  - Port: the local port of the connection on the server

The contents of that ORIGIN frame (and subsequent ones) allows the server to incrementally add new
origins to the Origin Set, as described in {{process}}.

The Origin Set is also affected by the 421 (Misdirected Request) response status code, defined in
{{!RFC7540}} Section 9.1.2. Upon receipt of a response with this status code, implementing clients
MUST create the ASCII serialisation of the corresponding request's origin (as per {{!RFC6454}},
Section 6.2) and remove it from the connection's Origin Set, if present.

Note that the Origin Set does not affect existing streams on a connection in any way.


## Authority, Push and Coalescing with ORIGIN {#authority}

{{!RFC7540}}, Section 10.1 uses both DNS and the presented TLS certificate to establish the origin
server(s) that a connection is authoritative for, just as HTTP/1.1 does in {{?RFC7230}}.
Furthermore, {{!RFC7540}} Section 9.1.1 explicitly allows a connection to be used for more than one
origin server, if it is authoritative. This affects what requests can be sent on the connection, both in HEADERS frame by the client and as PUSH_PROMISE frames from the server.

Upon receiving an ORIGIN frame on a connection, clients that implement this specification change
these behaviors in the following ways:

* Clients MUST NOT consult DNS to establish authority for origins in the Origin Set. The TLS certificate MUST be used to do so, as described in {{!RFC7540}} Section 9.1.1.

* Clients sending a new request SHOULD use an existing connection if the request's origin is in that connection's Origin Set, unless there are operational reasons for creating a new connection.

* Clients MUST use the Origin Set to determine whether a received PUSH_PROMISE is authoritative, as described in {{!RFC7540}}, Section 8.2.2.

Note that this does not prevent clients from performing other certificate checks as required or
allowed, either at connection time or when processing ORIGIN. See {{!RFC7540}} Section 9.1.1 for
more information.


# IANA Considerations

This specification adds an entry to the "HTTP/2 Frame Type" registry.

* Frame Type: ORIGIN
* Code: 0xb
* Specification: [this document]


# Security Considerations

Clients that blindly trust the ORIGIN frame's contents will be vulnerable to a large number of
attacks. See {{authority}} for mitigations.

Relaxing the requirement to consult DNS when determining authority for an origin means that an
attacker who possesses a valid certificate no longer needs to be on-path to redirect traffic to
them; instead of modifying DNS, they need only convince the user to visit another Web site, in
order to coalesce connections to the target onto their existing connection.

--- back


# Non-Normative Processing Algorithm {#algo}

The following algorithm illustrates how a client could handle received ORIGIN frames:

1. If the client is configured to use a proxy for the connection, ignore the frame and stop processing.
2. If the connection is not running under TLS, does not present Server Name Indication (SNI) {{!RFC6006}}, or the connection does not otherwise meet the requirements set by standards or the client implementation, ignore the frame and stop processing.
3. If the frame occurs upon any stream except stream 0, ignore the frame and stop processing.
4. If any of the flags 0x1, 0x2, 0x4 or 0x8 are set, ignore the frame and stop processing.
5. For each Origin field `origin_raw` in the frame payload:
   1. Parse `origin_raw` as an ASCII serialization of an origin ({{!RFC6454}}, Section 6.2) and let the result be `parsed_origin`. If parsing fails, skip to the next `origin_raw`.
   2. If the `scheme` of `parsed_origin` is not "https", skip to the next `origin_raw`.
   3. If the `host` of `parsed_origin` does not match a `subjectAltName` in the connection's presented certificate (using the wildcard rules defined in {{!RFC2818}}, Section 3.1), skip to the next `origin_raw`.
   4. If the `port` of `parsed_origin` does not match the connection's remote port, skip to the next `origin_raw`.
   5. Add `parsed_origin` to the Origin Set.

