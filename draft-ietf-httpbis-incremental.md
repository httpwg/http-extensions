---
title: "Incremental HTTP Messages"
docname: draft-ietf-httpbis-incremental-latest
category: std
wg: httpbis
ipr: trust200902
keyword: internet-draft
stand_alone: yes
pi: [toc, sortrefs, symrefs]
author:
 -
    fullname:
      :: 奥 一穂
      ascii: Kazuho Oku
    org: Fastly
    email: kazuhooku@gmail.com
 -
    fullname: Tommy Pauly
    organization: Apple
    email: tpauly@apple.com
 -
    fullname: Martin Thomson
    organization: Mozilla
    email: mt@lowentropy.net

normative:

informative:
  EXTRA-STATUS: RFC6585
  PROXY-STATUS: RFC9209
  SSE:
    target: https://html.spec.whatwg.org/multipage/server-sent-events.html
    title: Server-Sent Events
    author:
     -
        org: WHATWG



--- abstract

This document specifies the "Incremental" HTTP header field, which instructs
HTTP intermediaries to forward the HTTP message incrementally.


--- middle

# Introduction

HTTP {{!HTTP=RFC9110}} permits receivers to begin processing portions of HTTP
messages as they arrive, rather than requiring them to wait for the entire HTTP
message to be received before acting.

Some applications are specifically designed to take advantage of this
capability.

For example, Server-Sent Events {{SSE}} uses a long-running HTTP response, where
the server continually sends notifications as they become available.

In the case of Chunked Oblivious HTTP Messages
{{?CHUNKED-OHTTP=I-D.ietf-ohai-chunked-ohttp}}, the client opens an HTTP request
and incrementally sends application data, while the server can start responding
even before the HTTP request is fully complete. In this way, the HTTP
request-response pair could create what is, in effect, a bi-directional
communication channel.

Applications that rely on incremental delivery of data are fragile when HTTP intermediaries are involved.
This is because HTTP intermediaries are not only permitted but are frequently
deployed to buffer complete HTTP messages before forwarding them downstream
({{Section 7.6 of HTTP}}).

If such a buffering HTTP intermediary exists between the client and the server,
these applications may fail to function as intended.

In the case of Server-Sent Events, an intermediary that tries to buffer the HTTP
response completely before forwarding it could be left waiting indefinitely.
A client might never receive any portion of the response.

In the case of requests that involve any bi-directional exchange,
an intermediary that tries to buffer entire messages --
either request or response -- prevents any data from being delivered.

To help avoid such behavior, this document specifies the "Incremental" HTTP header
field, which instructs HTTP intermediaries to begin forwarding the HTTP message
downstream before receiving the complete message.


# Conventions and Definitions

{::boilerplate bcp14-tagged}

This document relies on structured field definitions
of Item and Boolean {{!STRUCTURED-FIELDS=RFC8941}}.


# The Incremental Header Field

The Incremental HTTP header field expresses the sender's intent for HTTP
intermediaries to start forwarding the message downstream before the entire
message is received.

The Incremental header field is defined as a structured field
{{STRUCTURED-FIELDS}} of type Item.  There is just one valid value, which is of
type Boolean: "?1".

~~~
Incremental = ?1
~~~

Upon receiving a header section that includes an Incremental header field with a
true value, HTTP intermediaries SHOULD NOT buffer the entire message before
forwarding it.  Instead, intermediaries SHOULD transmit the header section
downstream and continuously forward the bytes of the message body as they
arrive. As the Incremental header field indicates only how the message content is
to be forwarded, intermediaries can still buffer the entire header and trailer
sections of the message before forwarding them downstream.

The request to use incremental forwarding also applies to HTTP implementations.
Though most HTTP APIs provide the ability to incrementally transfer message content,
those that do not for any reason, SHOULD use the presence of the Incremental
header field to reduce or disable buffering.

The Incremental HTTP header field applies to each HTTP message. Therefore, if
both the HTTP request and response need to be forwarded incrementally, the
Incremental HTTP header field MUST be set for both the HTTP request and the
response.

The Incremental field is advisory. Intermediaries that are unaware of the field
or that do not support the field might buffer messages, even when explicitly
requested otherwise.  Clients and servers therefore cannot expect all
intermediaries to understand and respect a request to deliver messages
incrementally. Clients can rely on prior knowledge or probe for support on
individual resources.

The Incremental header field facilitates the establishment of a bidirectional
byte channel over HTTP, as its presence in both requests and responses instructs
intermediaries to forward early responses ({{Section 7.5 of HTTP}}) and to
transmit message contents incrementally in both directions.  However, when developing
bidirectional protocols over HTTP, Extended CONNECT {{?RFC8441}}{{?RFC9220}} is
generally more consistent with HTTP's architecture.


# Security Considerations

When receiving an incremental request, intermediaries might reject the request
due to security concerns. The following subsections explore typical scenarios
under which the intermediaries might reject requests.


## Permanent Rejection

Some intermediaries inspect the payload of an HTTP messages and forward them
only if the content is deemed safe. Any feature that depends on seeing the
entirety of the message in this way is incompatible with incremental delivery,
so these intermediaries need to reject requests unless the entire message is
received.

When an intermediary rejects an incremental message -- either a request or a
response -- due to security concerns with regard to the payload that the message
might convey, the intermediary SHOULD respond with a 501 Not Implemented error
with an incremental_refused Proxy-Status response header field
({{iana-considerations}}).


## Temporary Rejection

To conserve resources required to handle HTTP requests or connections, it is
common for intermediaries to impose limits on the maximum number of concurrent
HTTP requests that they forward, while buffering requests that exceed this
limit.

Such intermediaries could apply a more restrictive concurrency limit to requests
marked as incremental to ensure that capacity remains available for
non-incremental requests, even when the maximum number of incremental requests
is reached. This approach helps balance the processing of different types of
requests and maintains service availability across all requests.

When rejecting incremental requests due to reaching the concurrency limit,
intermediaries SHOULD respond with a 429 Too Many Requests error
({{Section 4 of EXTRA-STATUS}}),
accompanied by a connection_limit_reached Proxy-Status response header field
({{Section 2.3.12 of PROXY-STATUS}}).


## Handling of Small Packets

For performance and efficiency reasons, a small amount of buffering might be
used by intermediaries, even for incremental messages. Immediate forwarding
might be exploited to cause an intermediary to waste effort on many small
packets.  Enabling incremental delivery might instead set limits on the number
bytes that are buffered or the time that buffers are held before forwarding.
Any buffering could adversely affect application latency, even if it improves
efficiency.  In all cases, intermediaries cannot hold data in buffers
indefinitely, so data needs to be forwarded when either the time limit or the
byte limit is reached.


# IANA Considerations

An HTTP field named Incremental is registered
in the Hypertext Transfer Protocol (HTTP) Field Name Registry,
following the procedures in {{Section 18.4 of !HTTP=RFC9110}}.
The following values are registered:

Field Name:
: Incremental

Status:
: permanent

Structured Type:
: Item

Reference:
: This document

Comments:
: None
{: spacing="compact"}

An HTTP Proxy Error Type is registered in the HTTP Proxy Error Types registry as
shown below:

Name:
: incremental_refused

Description:
: The HTTP message contained the Incremental HTTP header field, but the
  intermediary refused to forward the message incrementally.

Extra Parameters:
: none

Recommended HTTP Status Code:
: 501

Response Only Generated By Intermediaries:
: true

Reference:
: this document

--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
