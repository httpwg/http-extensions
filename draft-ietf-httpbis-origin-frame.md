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

The ORIGIN frame type is 0xb (decimal 11).

~~~~
+-------------------------------+-------------------------------+
|         Origin-Len (16)       | Origin? (*)                 ...
+-------------------------------+-------------------------------+
~~~~

The ORIGIN frame's payload contains the following fields, sets of which may be repeated within the
frame to indicate multiple origins:

Origin-Len:
: An unsigned, 16-bit integer indicating the length, in octets, of the Origin field.

Origin:
: An optional sequence of characters containing the ASCII serialization of an origin ({{!RFC6454}}, Section 6.2) that the sender believes this connection is or could be authoritative for.

The ORIGIN frame defines the following flags:

CLEAR (0x1):
: Indicates that the Origin Set MUST be reset to an empty before processing the contents of the frame it occurs upon.

REMOVE (0x2): 
: Indicates that the origin(s) carried in the payload must be removed from the Origin Set, if present; if not present, it/they have no effect.


## The Origin Set {#set}

The set of origins (as per {{!RFC6454}}) that a given connection might be used for is known in this
specification as the Origin Set.

When a connection is first established, its Origin Set is defined to be the origin composed from:
  - Scheme: "https"
  - Host: the value sent in Server Name Indication {{!RFC6066}}
  - Port: the local port of the connection on the server

If SNI is not sent, the Origin Set is empty when the connection is established.

The ORIGIN frame allows the server to modify the Origin Set. In particular:

1. A server can add to its members by sending an ORIGIN frame (without any flags set);
2. A server can prune one or more origins from it by sending them in an ORIGIN frame with the REMOVE flag set;
3. A server can remove all its members and then add zero or more members by sending an ORIGIN frame with the CLEAR flag set and a payload containing the new origins.

Adding to the Origin Set (cases 1 and 3 above) does not imply that the connection is authoritative
for the added origins (in the sense of {{!RFC7540}}, Section 10.1) on its own; see {{authority}}.


## Establishing Authority and Coalescing with ORIGIN {#authority}

{{RFC7540}}, Section 10.1 uses both DNS and the presented TLS certificate to establish the
authority of an origin server, just as HTTP/1.1 does in {{RFC7230}}.

Upon receiving an ORIGIN frame on a connection, clients that implement this specification are
released from the requirement to establish authority for a given origin using DNS, for that
connection. However, they MUST still establish authority using the certificate, as described in
{{RFC7540}} Section 9.1.1.

Once such a frame is received, an implementing client MUST NOT use that connection for a given
origin unless it appears in the connection's Origin Set. Implementing clients SHOULD use a
connection for all origins which it is authoritative for, if they are included in its Origin Set.


## Processing ORIGIN Frames {#process}

The ORIGIN frame is a non-critical extension to HTTP/2. Endpoints that do not support this frame
can safely ignore it upon receipt.

When received by an implementing client, it is used to manipulate the Origin Set (see {{set}}).

The origin frame MUST be sent on stream 0; an ORIGIN frame on any other stream is invalid and MUST
be ignored.

The ORIGIN frame is processed hop-by-hop. An intermediary MUST NOT forward ORIGIN frames. Clients
configured to use a proxy MUST ignore any ORIGIN frames received from it.

The following algorithm illustrates how a client can handle received ORIGIN frames:

1. If the client is configured to use a proxy for the connection, ignore the frame and stop processing.
2. If the frame occurs upon any stream except stream 0, ignore the frame and stop processing.
3. If the CLEAR flag is set, remove all members from the Origin Set.
4. For each Origin field `origin_raw` in the frame payload:
   1. Parse `origin_raw` as an ASCII serialization of an origin ({{!RFC6454}}, Section 6.2) and let the result be `parsed_origin`. If parsing fails, skip to the next `origin_raw`.
   2. If the REMOVE flag is set, remove any member of the Origin Set that is the same as `parsed_origin` (as per {{!RFC6454}}, Section 5), and continue to the next `parsed_origin`.
   3. Otherwise, add `parsed_origin` to the Origin Set.


# Security Considerations

Clients that blindly trust the ORIGIN frame's contents will be vulnerable to a large number of
attacks.

--- back
