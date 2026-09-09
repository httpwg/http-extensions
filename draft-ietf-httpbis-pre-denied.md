---
title: The Purpose Declined HTTP Status Code
docname: draft-ietf-httpbis-pre-denied-latest
date: {DATE}
category: std

ipr: trust200902
keyword: Internet-Draft

stand_alone: yes
smart_quotes: no
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline]

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/pre-denied
  latest: "https://httpwg.org/http-extensions/draft-ietf-httpbis-pre-denied.html"

github-issue-label: pre-denied

entity:
  SELF: "RFC nnnn"
  CODE: "419"

author:
 -
    ins: M. Nottingham
    name: Mark Nottingham
    organization: Cloudflare
    postal:
      - Melbourne
    country: Australia
    email: mnot@mnot.net
    uri: https://mnot.net/

normative:
  HTTP: RFC9110
  HTTP-CACHING: RFC9111
  FETCH:
    target: https://fetch.spec.whatwg.org/
    title: Fetch
    author:
      -
        organization: WHAT Working Group
    date:


--- abstract

This specification defines an HTTP status code to indicate that the server
is denying a request based upon its declared purpose.

--- middle


# Introduction

{{FETCH}} introduces a mechanism whereby HTTP {{HTTP}} user agents can speculatively request a representation of a resource, in order to improve perceived performance.

In some circumstances, a server might have information that leads it to believe that sending a full
response will not improve performance, and could have negative impacts.

When this happens, it is common practice to use a 503 (Service Unavailable) status code. However, this has been observed to cause confusion: a server operator who sees a spike in that status code being sent tends to draw the conclusion that there is a server-side operational issue.

While other status codes (e.g., 403 (Forbidden)) could be used, they can also suffer (to varying degrees) from the same problem: being confused with an error, operational problem, or other condition.

This specification defines a new status code to specifically address this situation, making servers' behavior more legible to their operators. It does not introduce any new capability.

## Notational Conventions

{::boilerplate bcp14-tagged}

# The {{&CODE}} (Purpose Declined) Status Code

The {{&CODE}} (Purpose Declined) status code indicates that the server is refusing a request based upon its declared purpose.

A request's declared purpose is indicted by its Sec-Purpose header field {{FETCH}}.

This indication is only applicable to the associated request; future requests with the same purpose might or might not succeed.

Because responses with this status code are not intended to be displayed to a user, they SHOULD have zero-length content, and any content that is sent SHOULD be discarded.

Both origin servers and gateways acting on their behalf (e.g., Content Delivery Networks and so-called "reverse proxies") MAY generate this status code. Proxies (who are not acting on behalf of the origin server) SHOULD NOT generate it.

This status code is not heuristically cacheable (see {{Section 15.1 of HTTP}}). To avoid responses with this status code being reused by a cache, they SHOULD NOT be cacheable (see {{Section 3 of HTTP-CACHING}}).

# IANA Considerations

The following entry should be registered in the "HTTP Status Codes" registry:

* Code: {{&CODE}}
* Description: Purpose Declined
* Specification: {{&SELF}} (this document)

# Security Considerations

The security considerations of {{HTTP}} and {{FETCH}} apply. Conceivably, the use of this status code could leak information about the internal state of the server; caution should be exercised to assure that it does not.

--- back

