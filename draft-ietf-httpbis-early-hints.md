---
title: An HTTP Status Code for Indicating Hints
abbrev: Early Hints
docname: draft-ietf-httpbis-early-hints-latest
date: 2017
category: info

ipr: trust200902
area: General
workgroup: HTTP
keyword: Internet-Draft

stand_alone: yes
pi: [toc, docindent, sortrefs, symrefs, strict, compact, comments, inline]

author:
 -
    ins: K. Oku
    name: Kazuho Oku
    organization: DeNA Co., Ltd.
    email: kazuhooku@gmail.com

normative:
  RFC2119:
  RFC7230:
  RFC7231:
  RFC7540:

informative:
  Preload:
    title: Preload
    author:
      ins: I. Grigorik
    date: 2016-09-16
    target: https://w3c.github.io/preload/

--- abstract

This memo introduces an informational status code for HTTP that can be used for indicating hints to
help a client start making preparations for processing the final response.


--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org),
which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <https://httpwg.github.io/>; source code and issues list
for this draft can be found at <https://github.com/httpwg/http-extensions/labels/early-hints>.


--- middle

# Introduction

Most if not all of the web pages processed by a web browser contain links to external resources
that need to be fetched prior to rendering the documents. Therefore, it is beneficial to send such
links as early as possible in order to minimize the time spent until the browser becomes possible
to render the document. Link header of type "preload" ([Preload]) can be used to indicate such
links within the response headers of an HTTP response.

However, it is not always possible for an origin server to send a response immediately after
receiving a request. In fact, it is often the contrary. There are many deployments in which an
origin server needs to query a database before generating a response. It is also not unusual for an
origin server to delegate a request to an upstream HTTP server running at a distant location.

The dilemma here is that even though it is preferable for an origin server to send some headers as
soon as it receives a request, it cannot do so until the status code and the headers of the final
HTTP response is determined.

HTTP/2 ([RFC7540]) push can be used as a solution to the issue, but has its own limitations. The
resources that can be pushed using HTTP/2 are limited to those belonging to the same origin. Also,
it is impossible to send only the links of the resources using HTTP/2 push. Sending HTTP responses
for every resource is an inefficient way of using bandwidth, especially when a caching server
exists as an intermediary.

This memo defines a status code for sending an informational response ([RFC7231], section 6.2) that
contains headers that are likely to be included in the final response. A server can send the
informational response containing some of the headers to help the client start making preparations
for processing the final response, and then run time-consuming operations to generate the final
response. The informational response can also be used by an origin server to trigger HTTP/2 push at
an caching intermediary.

## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
[RFC2119].

# 103 Early Hints

This informational status code indicates the client that the server is likely to send a final
response with the headers included in the informational response.

A server MUST NOT include Content-Length, Transfer-Encoding, or any hop-by-hop headers ([RFC7230],
section 6.1) in the informational response using the status code.

A client MAY speculatively evaluate the headers included in the informational response while
waiting for the final response. For example, a client may recognize the link header of type preload
and start fetching the resource. However, the evaluation MUST NOT affect how the final response is
processed; the client must behave as if it had not seen the informational response.

An intermediary MAY drop the informational response. It MAY send HTTP/2 ([RFC7540]) push responses
using the information found in the informational response.

# Interoperatibility Issues

Clients may have issues handling Early Hints, since informational response is rarely used for
requests not including an Expect header ([RFC7231], section 5.1.1). Therefore, it is desirable to
negotiate the capability to use the status code.

# Security Considerations

TBD

# IANA Considerations

If Early Hints is standardized, the HTTP Status Codes Registry should be updated with the following
entries:

* Code: 103
* Description: Early Hints
* Specification: this document

# Acknowledgements

Thanks to Tatsuhiro Tsujikawa for coming up with the idea of sending the link headers using an
informational response.
