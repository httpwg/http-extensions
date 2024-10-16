---
title: The ORIGIN Extension in HTTP/3
abbrev: ORIGIN in HTTP/3
number: 9412
docname: draft-ietf-httpbis-origin-h3-latest
date: 2023-06
category: std

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTPbis
keyword: Internet-Draft

stand_alone: yes
pi: [toc, sortrefs, symrefs]

author:
  -
    ins: M. Bishop
    name: Mike Bishop
    organization: Akamai
    email: mbishop@evequefou.be

normative:
  RFC9113:
    display: HTTP/2
  RFC9114:
    display: HTTP/3

informative:
  QUIC-TRANSPORT:
    RFC9000


--- abstract

The ORIGIN frame for HTTP/2 is equally applicable to HTTP/3, but it
needs to be separately registered. This document describes the ORIGIN
frame for HTTP/3.

--- middle

# Introduction {#problems}

Existing RFCs define extensions to HTTP/2 {{RFC9113}} that remain useful in
HTTP/3. {{Section A.2 of RFC9114}} describes the required updates for HTTP/2
frames to be used with HTTP/3.

{{!ORIGIN=RFC8336}} defines the HTTP/2 ORIGIN frame, which indicates what
origins are available on a given connection.  It defines a single HTTP/2 frame
type.

## Notational Conventions

{::boilerplate bcp14-tagged}

The frame diagram in this document uses the format defined in {{Section 1.3 of
QUIC-TRANSPORT}} to illustrate the order and size of fields.

# The ORIGIN HTTP/3 Frame {#frame-origin}

The ORIGIN HTTP/3 frame allows a server to indicate what origin or origins
{{?RFC6454}} the server would like the client to consider as one or more members
of the Origin Set ({{Section 2.3 of ORIGIN}}) for the connection within which it
occurs.

The semantics of the frame payload are identical to those of the HTTP/2 frame
defined in {{!ORIGIN}}. Where HTTP/2 reserves stream 0 for frames related to the
state of the connection, HTTP/3 defines a pair of unidirectional streams called
"control streams" for this purpose.

Where {{ORIGIN}} indicates that the ORIGIN frame is sent on stream 0, this
should be interpreted to mean the HTTP/3 control stream: that is,
the ORIGIN frame is sent from servers to clients on the server's control stream.

HTTP/3 does not define a Flags field in the generic frame layout. As no flags
have been defined for the ORIGIN frame, this specification does not define a
mechanism for communicating such flags in HTTP/3.

## Frame Layout

The ORIGIN frame has a layout that is nearly identical to the
layout used in HTTP/2; the information is restated here for clarity.  The ORIGIN
frame type is 0x0c (decimal 12), as in HTTP/2. The payload contains zero or more
instances of the Origin-Entry field.

~~~~~ ascii-art
HTTP/3 Origin-Entry {
  Origin-Len (16),
  ASCII-Origin (..),
}

HTTP/3 ORIGIN Frame {
  Type (i) = 0x0c,
  Length (i),
  Origin-Entry (..) ...,
}
~~~~~
{: title="ORIGIN Frame Layout"}

An Origin-Entry is a length-delimited string. Specifically, it contains two
fields:

Origin-Len:
: An unsigned, 16-bit integer indicating the length, in octets, of
the ASCII-Origin field.

ASCII-Origin:
: An OPTIONAL sequence of characters containing the ASCII serialization of an
  origin ({{RFC6454, Section 6.2}}) that the sender asserts this connection is
  or could be authoritative for.

# Security Considerations {#security}

This document introduces no new security considerations beyond those discussed
in {{!ORIGIN}} and {{RFC9114}}.

# IANA Considerations {#iana}

This document registers a frame type in the "HTTP/3 Frame Types" registry
defined by {{RFC9114}}, located at
\<https://www.iana.org/assignments/http3-parameters/>.

Value:
: 0x0c

Frame Type:
: ORIGIN

Status:
: permanent

Reference:
: {{frame-origin}}

Date:
: 2023-03-14

Change Controller:
: IETF

Contact:
: HTTP WG \<ietf-http-wg@w3.org>

--- back
