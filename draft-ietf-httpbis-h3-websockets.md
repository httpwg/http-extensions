---
title: "Bootstrapping WebSockets with HTTP/3"
docname: draft-ietf-httpbis-h3-websockets-latest
category: std

ipr: trust200902
area: ART
workgroup: HTTP
keyword: Internet-Draft
venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/h3-websockets
github-issue-label: h3-websockets
stand_alone: yes
smart_quotes: no
pi: [toc, sortrefs, symrefs]

author:
 -
    name: Ryan Hamilton
    organization: Google
    email: rch@google.com

normative:
  HTTP3: I-D.draft-ietf-quic-http-34

informative:


--- abstract

The mechanism for running the WebSocket Protocol over a single stream
of an HTTP/2 connection is equally applicable to HTTP/3, but the HTTP
version-specific details need to be specified. This document describes
how the mechanism is adapted for HTTP/3.

--- middle

# Introduction

{{!RFC8441}} defines an extension to HTTP/2 which is also useful in HTTP/3.
This extension makes use of an HTTP/2 setting.  {{Appendix A.3 of HTTP3}}
describes the required updates for HTTP/2 settings to be used with HTTP/3.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Websockets Upgrade over HTTP/3

{{!RFC8441}} defines a mechanism for running the WebSocket Protocol
{{!RFC6455}} over a single stream of an HTTP/2 connection. It defines
an Extended CONNECT method which specifies a new ":protocol" pseudo
header field and new semantics for the ":path" and ":authority" pseudo
header fields. It also defines a new HTTP/2 setting sent by a server to
allow the client to use  Extended CONNECT.

The HTTP/3 stream closure is also analogous to the TCP connection
closure of {{!RFC6455}}. Orderly TCP-level closures are represented as
a FIN bit on the stream ({{Section 4.2 of HTTP3}}). RST exceptions are
represented with an stream error ({{Section 8 of HTTP3}}) of type
H3_REQUEST_CANCELLED ({{Section 8.1 of HTTP3}}).

The semantics of the headers and setting are identical to those
in HTTP/2 as defined {{!RFC8441}}. {{Appendix A.3 of HTTP3}} requires that
HTTP/3 settings be registered separately for HTTP/3. The
SETTINGS_ENABLE_CONNECT_PROTOCOL value is 0x08 (decimal 8), as in HTTP/2.

If a server which advertises support for Extended CONNECT but receives an
Extended CONNECT request with a ":protocol" value that is unknown or is
not supported, the server SHOULD respond to the request with a 501 status
code ({{Section 6.6.2 of !RFC7231}}).

# Security Considerations

This document introduces no new security considerations beyond those
discussed in {{!RFC8841}}.

# IANA Considerations

This document registers a new setting in the "HTTP/3 Settings"
registry ([HTTP3]).


| -------------------------------- | ------- | -------------------- | ------- |
| Setting Name                     |  Value  | Specification        | Default |
| -------------------------------- | :-----: | -------------------- | ------- |
| SETTINGS_ENABLE_CONNECT_PROTOCOL |  0x08   | This document        | 0       |
| -------------------------------- | ------- | -------------------- | ------- |

--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
