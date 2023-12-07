---
title: HTTP Cache Groups
abbrev:
docname: draft-ietf-httpbis-cache-groups-latest
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
  repo: https://github.com/httpwg/http-extensions/labels/cache-groups
github-issue-label: cache-groups

author:
 -
    ins: M. Nottingham
    name: Mark Nottingham
    organization:
    postal:
      - Prahran
    country: Australia
    email: mnot@mnot.net
    uri: https://www.mnot.net/

normative:
  HTTP: RFC9110
  HTTP-CACHING: RFC9111
  STRUCTURED-FIELDS: RFC8941

informative:
  TARGETED: RFC9213

entity:
  SELF: "RFC nnnn"

--- abstract

This specification introduces a means of describing the relationships between stored responses in HTTP caches, "grouping" them by associating a stored response with one or more opaque strings.

--- middle


# Introduction

HTTP caching {{HTTP-CACHING}} operates at the granularity of a single resource; the freshness of one stored response does not affect that of others. This granularity can make caching more efficient -- for example, when a page is composed of many assets that have different requirements for caching.

However, there are also cases where the relationship between stored responses could be used to improve cache efficiency.

For example, it's common for a set of closely-related resources to be deployed on a site, such as is the case for many JavaScript libraries and frameworks. These resources are typically deployed with long freshness lifetimes for caching. When that period passes, the cache will need to revalidate each stored response in a short period of time. Grouping these resources can be used to allow a cache to consider them all as being revalidated when any single response in the group is revalidated, removing the need to revalidate all of them individually and avoiding the associated overhead.

Likewise, when some resources change, it implies that other resources may have also changed. This might be because a state-changing request has side effects on other resources, or it might be purely for administrative convenience (e.g., "invalidate this part of the site"). Grouping responses together provides a dedicated way to express these relationships, instead of relying on things like URL structure.

In addition to sharing revalidation and invalidation events, the relationships indicated by grouping can also be used by caches to optimise their operation; for example, it could be used to inform the operation of cache eviction algorithms.

{{cache-groups}} introduces a means of describing the relationships between a set of stored responses in HTTP caches by associating them with one or more opaque strings. It also describes how caches can use that information to apply revalidation and invalidation events to members of a group.

{{cache-group-invalidation}} introduces one new source of such events: a HTTP response header that allows a state-changing response to trigger a group invalidation.

These mechanisms operate within a single cache, across the stored responses associated with a single origin server. They do not address this issues of synchronising state between multiple caches (e.g., in a hierarchy or mesh), nor do they facilitate association of stored responses from disparate origins.


## Notational Conventions

{::boilerplate bcp14-tagged}

This specification uses the following terminology from {{STRUCTURED-FIELDS}}: List, String, Parameter.


# The Cache-Groups Response Header Field {#cache-groups}

The Cache-Groups HTTP Response Header is a List of Strings {{STRUCTURED-FIELDS}}. Each member of the list is an opaque value that identifies a group that the response belongs to.

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/javascript
Cache-Control: max-age=3600
Cache-Groups: "ExampleJS";revalidate, "scripts"
~~~

This specification defines one Parameter for Cache-Groups, "revalidate", that indicates that the resources associated with that group share revalidation; see {{revalidation}}.

The ordering of members of Cache-Groups is not significant.


## Identifying Grouped Responses {#identify}

Two responses stored in the same cache are considered to have the same group when all of the following conditions are met:

1. They both contain a Cache-Groups response header field that contains the same String (in any position in the List), when compared character-by-character.
2. The both share the same URI origin (per {{Section 4.3.1 of HTTP}}).
3. If being considered for revalidation ({{revalidation}}), they both have the "revalidate" Parameter.


## Cache Behaviour

### Revalidation {#revalidation}

A cache that successfully revalidates a stored response MAY consider any stored responses that share a group (per {{identify}}) as also being revalidated at the same time.

Cache extensions can explicitly strengthen the requirement above. For example, a targeted cache control header field {{TARGETED}} might specify that caches processing it are required to revalidate such responses.


### Invalidation {#invalidation}

A cache that invalidates a stored response MAY invalidate any stored responses that share groups (per {{identify}}) with that response.

Cache extensions can explicitly strengthen the requirement above. For example, a targeted cache control header field {{TARGETED}} might specify that caches processing it are required to invalidate such responses.


# The Cache-Group-Invalidation Response Header Field {#cache-group-invalidation}

The Cache-Group-Invalidation response header field is a List of Strings {{STRUCTURED-FIELDS}}. Each member of the list is an opaque value that identifies a group that the response invalidates, per {{invalidation}}.

For example, a POST request that has side effects on two cache groups could indicate that stored responses associated with either or both of those groups should be invalidated with:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: text/html
Cache-Group-Invalidation: "eurovision-results", "kylie-minogue"
~~~

The Cache-Group-Invalidation header field MUST be ignored on responses to requests that have a safe method (e.g., GET; see {{Section 9.2.1 of HTTP}}.

A cache that receives a Cache-Group-Invalidation header field on a response to an unsafe request MAY invalidate any stored responses that share groups (per {{identify}}) with any of the listed groups.


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

_TBD_


--- back

# Acknowledgements

Thanks to Stephen Ludin for his review and suggestions.

