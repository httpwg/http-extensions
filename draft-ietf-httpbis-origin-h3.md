---
title: The ORIGIN Extension in HTTP/3
abbrev: ORIGIN in HTTP/3
docname: draft-ietf-httpbis-origin-h3-latest
date: {DATE}
category: std

ipr: trust200902
area: Applications
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
  HTTP2:
    RFC9113
  HTTP3:
    RFC9114

informative:


--- abstract

The ORIGIN frame for HTTP/2 is equally applicable to HTTP/3, but
needs to be separately registered. This document describes the ORIGIN
frame for HTTP/3.

--- middle

# Introduction {#problems}

Existing RFCs define extensions to HTTP/2 {{HTTP2}} which remain useful in HTTP/3.
{{Section A.2.3 of HTTP3}} describes the required updates
for HTTP/2 frames to be used with HTTP/3.

{{!ORIGIN=RFC8336}} defines the HTTP/2 ORIGIN frame, which indicates what
origins are available on a given connection.  It defines a single HTTP/2 frame
type.

# The ORIGIN HTTP/3 Frame {#frame-origin}

The ORIGIN HTTP/3 frame allows a server to indicate what origin(s)
({{?RFC6454}}) the server would like the client to consider as members of the
Origin Set ({{Section 2.3 of ORIGIN}}) for the connection within which it
occurs.

Where HTTP/2 reserves Stream 0 for frames related to the state of the
connection, HTTP/3 defines a pair of unidirectional streams called "control
streams" for this purpose.  Where {{ORIGIN}} indicates that the ORIGIN frame
should be sent on Stream 0, this should be interpreted to mean the HTTP/3
control stream.  The ORIGIN frame is sent from servers to clients on the
server's control stream.

The layout and semantics of the frame payload are identical to those of the
HTTP/2 frame defined in {{!ORIGIN}}.  The ORIGIN frame type is 0xc (decimal 12),
as in HTTP/2.

# Security Considerations {#security}

This document introduces no new security considerations beyond those discussed
in {{!ORIGIN}} and {{HTTP3}}.

# IANA Considerations {#iana}

This document registers a frame type in the "HTTP/3 Frame Type"
registry ({{HTTP3}}).

| ---------------- | ------ | -------------------------- |
| Frame Type       | Value  | Specification              |
| ---------------- | :----: | -------------------------- |
| ORIGIN           |  0xc   | {{frame-origin}}           |
| ---------------- | ------ | -------------------------- |
{: #iana-frame-table title="Registered HTTP/3 Frame Types"}

--- back
