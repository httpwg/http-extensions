---
title: HTTP Cache Groups
abbrev:
docname: draft-ietf-httpbis-cache-groups-latest
date: {DATE}
category: std

ipr: trust200902
keyword: HTTP, Caching, Invalidation
workgroup: HTTP
area: Web and Internet Transport

stand_alone: yes
smart_quotes: no
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline]

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/cache-groups
github-issue-label: cache-groups

author:
 -
    ins: M. Nottingham
    name: Mark Nottingham
    organization: Cloudflare
    postal:
      - Melbourne
    country: Australia
    email: mnot@mnot.net
    uri: https://www.mnot.net/

normative:
  HTTP: RFC9110
  HTTP-CACHING: RFC9111
  STRUCTURED-FIELDS: RFC9651

informative:
  TARGETED: RFC9213

entity:
  SELF: "RFC nnnn"

--- abstract

This specification introduces a means of describing the relationships between stored responses in HTTP caches, grouping them by associating a stored response with one or more strings.

--- middle


# Introduction

HTTP caching {{HTTP-CACHING}} operates at the granularity of a single resource; the freshness of one stored response does not affect that of others. This granularity can make caching more efficient -- for example, when a page is composed of many assets that have different requirements for caching.

However, there are also cases where the relationship between stored responses could be used to improve cache efficiency.

For example, it is often necessary to invalidate a set of related resources. This might be because a state-changing request has side effects on other resources, or it might be purely for administrative convenience (e.g., "invalidate this part of the site"). Grouping responses together provides a dedicated way to express these relationships, instead of relying on things like URL structure.

In addition to sharing invalidation events, the relationships indicated by grouping can also be used by caches to optimise their operation (e.g., to inform the operation of cache eviction algorithms).

{{cache-groups}} introduces a means of describing the relationships between stored responses in HTTP caches, by associating those responses with one or more groups that reflect those relationships. It also describes how caches can use that information to apply invalidation events to members of a group.

{{cache-group-invalidation}} introduces one new source of such events: a HTTP response header field that allows a state-changing response to trigger a group invalidation.

These mechanisms operate within a single cache, across the stored responses associated with a single origin server (see {{identify}}). They do not address the issues of synchronising state between multiple caches (e.g., in a hierarchy or mesh), nor do they facilitate association of stored responses from disparate origins.


## Notational Conventions

{::boilerplate bcp14-tagged}

This specification uses the following terminology from {{STRUCTURED-FIELDS}}: List, String, Parameter.


# The Cache-Groups Response Header Field {#cache-groups}

The Cache-Groups HTTP response header field is a List of Strings ({{Sections 3.1 and 3.3.3 of STRUCTURED-FIELDS}}). Each member of the List is a value that identifies a group that the response belongs to. These Strings are opaque -- while they might have some meaning to the server that creates them, the cache does not have any insight into their structure or content (beyond uniquely identifying a group).

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/javascript
Cache-Control: max-age=3600
Cache-Groups: "scripts"
~~~

The ordering of members is not significant. Unrecognised Parameters are to be ignored.

Implementations MUST support at least 32 groups in a field value, with up to at least 32 characters in each member. Note that generic limitations on HTTP field lengths may constrain the size of this field value in practice.

## Identifying Grouped Responses {#identify}

Two responses stored in the same cache are considered to belong to the same group when all of the following conditions are met:

1. They both contain a Cache-Groups response header field that contains the same String (in any position in the List), when compared character-by-character (case sensitive).
2. They both share the same URI origin (per {{Section 4.3.1 of HTTP}}).


## Cache Behaviour

### Invalidation {#invalidation}

A cache that invalidates a stored response MAY invalidate any stored responses that share groups (per {{identify}}) with that response. Note that further grouped invalidations are not triggered by a grouped invalidation; i.e., this mechanism does not cascade.

Cache extensions can explicitly strengthen the requirement above. For example, a targeted cache control header field {{TARGETED}} might specify that caches processing it are required to invalidate such responses.


# The Cache-Group-Invalidation Response Header Field {#cache-group-invalidation}

The Cache-Group-Invalidation response header field is a List of Strings ({{Sections 3.1 and 3.3.3 of STRUCTURED-FIELDS}}). Each member of the List is a value that identifies a group that the response invalidates, per {{invalidation}}.

For example, following a POST request that has side effects on two cache groups, the corresponding response could indicate that stored responses associated with either or both of those groups should be invalidated with:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: text/html
Cache-Group-Invalidation: "eurovision-results", "australia"
~~~

The Cache-Group-Invalidation header field MUST be ignored on responses to requests that have a safe method (e.g., GET; see {{Section 9.2.1 of HTTP}}).

A cache that receives a Cache-Group-Invalidation header field on a response to an unsafe request MAY invalidate any stored responses that share groups (per {{identify}}) with any of the listed groups.

Cache extensions can explicitly strengthen the requirement above. For example, a targeted cache control header field {{TARGETED}} might specify that caches processing it are required to respect the Cache-Group-Invalidation signal.

The ordering of members is not significant. Unrecognised Parameters are to be ignored.

Implementations MUST support at least 32 groups in a field value, with up to at least 32 characters in each member. Note that generic limitations on HTTP field lengths may constrain the size of this field value in practice.

# IANA Considerations

IANA should perform the following tasks:

## HTTP Field Names

Enter the following into the Hypertext Transfer Protocol (HTTP) Field Name Registry:

- Field Name: Cache-Groups
- Status: permanent
- Reference: {{&SELF}}
- Comments:

- Field Name: Cache-Group-Invalidation
- Status: permanent
- Reference: {{&SELF}}
- Comments:


# Security Considerations

This mechanism allows resources that share an origin to invalidate each other. Because of this,
origins that represent multiple parties (sometimes referred to as "shared hosting") might allow
one party to group its resources with those of others, or to send signals which have side effects upon them.

Shared hosts that wish to mitigate these risks can control access to the header fields defined in this specification.


--- back

# Acknowledgements

Thanks to Stephen Ludin for his review and suggestions.

