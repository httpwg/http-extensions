---
title: The ORIGIN HTTP/2 Frame
abbrev: ORIGIN Frames
docname: draft-ietf-httpbis-origin-frame-latest
date: 2016
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
    uri: http://www.mnot.net/
 -
    ins: E. Nygren
    name: Erik Nygren
    organization: Akamai
    email: nygren@akamai.com

normative:
  RFC2119:
  RFC6454:
  RFC7540:

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

HTTP/2 {{RFC7540}} allows clients to coalesce different origins {{RFC6454}} onto the same
connection when certain conditions are met. In some cases, the server is not authoritative for a
coalesced origin, so the 421 (Misdirected Request) status code ({{RFC7540}}, Section 9.1.2) was defined.

Using a status code in this manner allows clients to recover from misdirected requests, but at the
penalty of adding latency. To address that, this specification defines a new HTTP/2 frame type,
"ORIGIN", to allow servers to indicate what origins a connection is authoritative for.

## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
{{RFC2119}}.

# The ORIGIN HTTP/2 Frame

The ORIGIN HTTP/2 frame ({{RFC7540}}, Section 4) indicates what origin(s) {{RFC6454}} the sender
considers this connection authoritative for (in the sense of {{RFC7540}}, Section 10.1).

The ORIGIN frame is a non-critical extension to HTTP/2. Endpoints that do not support this frame
can safely ignore it.

It MUST occur on stream 0; an ORIGIN frame on any other stream is invalid and MUST be ignored.

When received by a client, it can be used to inform HTTP/2 connection coalescing (see {{RFC7540}},
Section 9.1.1), but does not relax the requirement there that the server is authoritative.

If multiple ORIGIN frames are received on the same connection, only the most recent is to be
considered current.

Once an ORIGIN frame has been received and processed, clients that implement this specification
SHOULD NOT use that connection for a given origin if it did not appear within the current ORIGIN
frame.



The ORIGIN frame type is 0xb (decimal 11).

~~~~
+-------------------------------+-------------------------------+
|         Origin-Len (16)       | Origin? (*)                 ...
+-------------------------------+-------------------------------+
~~~~

The ORIGIN frame contains the following fields, sets of which may be
	repeated within the frame to indicate multiple origins:

Origin-Len:
: An unsigned, 16-bit integer indicating the length, in octets, of the Origin field.

Origin:
: An optional sequence of characters containing the ASCII serialization of an origin ({{RFC6454}}, Section 6.2) that the sender believes this connection is authoritative for.

The ORIGIN frame does not define any flags. It can contain one or more Origin-Len/Origin pairs.

The ORIGIN frame is processed hop-by-hop. An intermediary must not forward ORIGIN frames.

Clients configured to use a proxy MUST ignore any ORIGIN frames received from it.


# Security Considerations

Clients that blindly trust the ORIGIN frame's contents will be vulnerable to a large number of
attacks; hence the reinforcement that this specification does not relax the requirement for server
authority in {{RFC7540}}, Section 10.1.

--- back
