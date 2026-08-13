---
title: The No-Vary-Search HTTP Caching Extension
abbrev: No-Vary-Search
category: std

docname: draft-ietf-httpbis-no-vary-search-latest
submissiontype: IETF
number:
date:
consensus: true
v: 3
area: "Web and Internet Transport"
workgroup: "HyperText Transfer Protocol"
keyword:
 - http
 - caching
venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/no-vary-search
  latest: "https://httpwg.org/http-extensions/draft-ietf-httpbis-no-vary-search.html"
github-issue-label: no-vary-search

author:
 -
    fullname: Domenic Denicola
    organization: Google LLC
    email: d@domenic.me
 -
    fullname: Jeremy Roman
    organization: Google LLC
    email: jbroman@chromium.org
 -
    fullname: Nidhi Jaju
    role: editor
    organization: Google LLC
    email: nidhijaju@chromium.org

normative:
  URI: RFC3986
  HTTP: RFC9110
  HTTP-CACHING: RFC9111
  STRUCTURED-FIELDS: RFC9651
  WHATWG-ENCODING:
   target: https://encoding.spec.whatwg.org/
   title: Encoding Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
   ann: WHATWG
  WHATWG-INFRA:
   target: https://infra.spec.whatwg.org/
   title: Infra Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
      -
         ins: D. Denicola
         name: Domenic Denicola
         org: Google LLC
   ann: WHATWG
  WHATWG-URL:
   target: https://url.spec.whatwg.org/
   title: URL Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
   ann: WHATWG

informative:
  HTML:
   target: https://html.spec.whatwg.org/
   title: HTML Living Standard
   author:
      -
         ins: A. van Kesteren
         name: Anne van Kesteren
         org: Apple Inc.
   ann: WHATWG
  NAV-TRACKING-MITIGATIONS:
   target: https://privacycg.github.io/nav-tracking-mitigations/
   title: Navigational-Tracking Mitigations
   author:
      -
         ins: P. Snyder
         name: Pete Snyder
         org: Brave Software, Inc.
      -
         ins: J. Yasskin
         name: Jeffrey Yasskin
         org: Google LLC
   ann: W3C Privacy CG
  ORIGIN: RFC6454

--- abstract

This specification defines an extension to HTTP Caching, changing how the URI query component impacts caching. It introduces the `"No-Vary-Search"` response header field, which allows origin servers to signal to caches that certain parts of the query component do not semantically affect the served response and can be ignored for cache matching purposes.

--- middle

# Introduction

HTTP caching {{HTTP-CACHING}} is based on reusing resources which match across a number of cache keys, with the most important one being the presented target URI ({{Section 7.1 of HTTP}}). However, sometimes multiple URIs can represent the same resource. This leads to caches not always being as helpful as they could be: if the cache contains a response under one URI, but the response is then requested under another, the cached version will be ignored.

The "No-Vary-Search" response header field defines a caching extension, as described in {{Section 4 of HTTP-CACHING}}, that tackles a specific subset of this general problem, for when different URIs that differ only in their query component identify the same resource. It allows resources to declare that some or all parts of the query component do not semantically affect the served response, and thus can be ignored for cache matching purposes. This is achieved by interpreting the query component as a sequence of parameters encoded using the `application/x-www-form-urlencoded` format {{WHATWG-URL}}. For example, if the order of the parameters within the query component does not affect which resource is identified, this is indicated using

~~~~http-message
No-Vary-Search: key-order
~~~~

If specific query parameters (e.g., ones indicating something for analytics) do not semantically affect the served resource, this is indicated using

~~~~http-message
No-Vary-Search: params=("utm_source" "utm_medium" "utm_campaign")
~~~~

And if the resource instead wants to take an allowlist-based approach, where only certain known query parameters semantically affect the served response, they can use

~~~~http-message
No-Vary-Search: except=("productId")
~~~~

Note that "cache busting", the practice of changing a part of the query component to create a distinct cache key and force retrieval of a newer response, can be made ineffective by the `"No-Vary-Search"` response header field.

{{header-definition}} defines the new `"No-Vary-Search"` response header field, using the {{STRUCTURED-FIELDS}} framework. {{data-model}} and {{parsing}} illustrate the data model for how the field value can be represented in specifications, and the process for parsing the raw output from the structured field parser into that data model. {{comparing}} gives the key algorithm for comparing if two URLs are equivalent under the influence of the header field; notably, it leans on the decomposition of the query component into keys and values given by the [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#concept-urlencoded) format specified in {{WHATWG-URL}}. (As such, this header field is not useful for URLs whose query component does not follow that format.) Finally, {{caching}} explains how to extend {{Section 4 of HTTP-CACHING}} to take this new equivalence into account.

From a deployment perspective, this extension is implemented by HTTP caches, including browser caches, content delivery networks, and forward proxies. Origin servers send the `"No-Vary-Search"` response header field to provide instructions to these caches. Caches that implement this extension use these instructions to determine when a previously stored response can be safely reused for a new request, even if the query components of the target URIs differ.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

In this document, the terms "URI" and "URL" are used interchangeably, depending on context. "URI" is used in the context of {{URI}}, {{HTTP}}, and {{HTTP-CACHING}}, whereas "URL" is used in the context of the algorithms specified in {{WHATWG-URL}}.

The term "query parameters" in this document refers to the keys and values resulting from parsing a URL's query component using the [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#concept-urlencoded) format {{WHATWG-URL}}.

This document also adopts some conventions and notation typical in WHATWG and W3C usage, especially as it relates to algorithms. See {{WHATWG-INFRA}}, and in particular:

* its definition of lists, including the list literal notation « 1, 2, 3 ».
* its definition of strings, including their representation as code units.

(Other concepts used are called out using inline references.)

# HTTP header field definition {#header-definition}

The `"No-Vary-Search"` response header field is a structured field {{STRUCTURED-FIELDS}} whose value MUST be a dictionary ({{Section 3.2 of STRUCTURED-FIELDS}}).

It has the following constraints:

* If present, the `key-order` entry's value MUST be a boolean ({{Section 3.3.6 of STRUCTURED-FIELDS}}).
* If present, the `params` entry's value MUST be an inner list of strings ({{Section 3.1.1 of STRUCTURED-FIELDS}}).
* If present, the `except` entry's value MUST be an inner list of strings ({{Section 3.1.1 of STRUCTURED-FIELDS}}).
* The `except` entry MUST NOT be present if the `params` entry is also present.

The dictionary MAY contain entries whose keys are not one of `key-order`, `params`, and `except`, but their meaning is not defined by this specification. Implementations of this specification will ignore such entries (but future documents might assign meaning to such entries). Future extensions to this dictionary MUST NOT restrict the set of URIs that are considered equivalent; they can only expand it. If a future extension requires restricting equivalence, it MUST be deployed as a new HTTP header field to ensure safety.

The `"No-Vary-Search"` response header field is set by origin servers. Intermediaries MUST NOT insert, delete, or modify the field's value unless they are acting as the origin server for that response.

{:aside}
> A parsing algorithm is defined in {{obtain-a-url-variation-config}}.

# Data model {#data-model}

A _URL variation config_ consists of the following:

{: vspace="0"}
no-vary params
: either the special value __wildcard__ or a list of strings

vary params
: either the special value __wildcard__ or a list of strings

vary on key order
: a boolean

(((!default URL variation config)))
The _default URL variation config_ is a URL variation config whose no-vary params is an empty list, vary params is __wildcard__, and vary on key order is true.

*[default URL variation config]:

The obtain a URL variation config algorithm ({{obtain-a-url-variation-config}}) ensures that all URL variation configs obey the following constraints:

* vary params is a list if and only if the no-vary params is __wildcard__; and
* no-vary params is a list if and only if the vary params is __wildcard__.

# Parsing {#parsing}

## Parse a URL variation config {#parse-a-url-variation-config}

*[parse a URL variation config]: #parse-a-url-variation-config

(((!parse a URL variation config)))
To _parse a URL variation config_ given _value_:

1. If _value_ is null, then return the default URL variation config.
1. Let _result_ be a new URL variation config.
1. Set _result_'s vary on key order to true.
1. If _value_\["`key-order`"] exists:
    1. Let _keyOrderValue_ be the `item_or_inner_list` component of the tuple _value_\["`key-order`"] (ignoring any parameters).
    1. If _keyOrderValue_ is not a boolean, then return the default URL variation config.
    1. Set _result_'s vary on key order to the boolean negation of _keyOrderValue_.
1. If both _value_\["`params`"] and _value_\["`except`"] exist, then return the default URL variation config.
1. If neither _value_\["`params`"] nor _value_\["`except`"] exists:
    1. Set _result_'s no-vary params to an empty list.
    1. Set _result_'s vary params to __wildcard__.
1. If _value_\["`params`"] exists:
    1. Let _paramsValue_ be the `item_or_inner_list` component of the tuple _value_\["`params`"] (ignoring any parameters).
    1. If _paramsValue_ is not an inner list, then return the default URL variation config.
    1. Let _paramsList_ be a list containing the `bare_item` component of each tuple in _paramsValue_ (ignoring any parameters).
    1. If any item in _paramsList_ is not a string, then return the default URL variation config.
    1. Set _result_'s no-vary params to the result of applying parse a key ({{parse-a-key}}) to each item in _paramsList_.
    1. Set _result_'s vary params to __wildcard__.
1. Otherwise, if _value_\["`except`"] exists:
    1. Let _exceptValue_ be the `item_or_inner_list` component of the tuple _value_\["`except`"] (ignoring any parameters).
    1. If _exceptValue_ is not an inner list, then return the default URL variation config.
    1. Let _exceptList_ be a list containing the `bare_item` component of each tuple in _exceptValue_ (ignoring any parameters).
    1. If any item in _exceptList_ is not a string, then return the default URL variation config.
    1. Set _result_'s vary params to the result of applying parse a key ({{parse-a-key}}) to each item in _exceptList_.
    1. Set _result_'s no-vary params to __wildcard__.
1. Return _result_.

{:aside}
> In general, this algorithm is strict and tends to return the default URL variation config whenever it sees something it doesn't recognize. This is because the default URL variation config behavior will just cause fewer cache hits, which is an acceptable fallback behavior.

{:aside}
> The input to this algorithm is generally obtained by parsing a structured field ({{Section 4.2 of STRUCTURED-FIELDS}}) using field_type "dictionary".

## Obtain a URL variation config {#obtain-a-url-variation-config}

*[obtain a URL variation config]: #obtain-a-url-variation-config

(((!obtain a URL variation config)))
To _obtain a URL variation config_ given an HTTP response ({{Section 3.4 of HTTP}}) _response_:

1. Let _fieldValue_ be the result of parsing the `"No-Vary-Search"` response header field from _response_ as a Dictionary ({{Section 4.2 of STRUCTURED-FIELDS}}). If parsing fails or the field is absent, let _fieldValue_ be null.
1. Return the result of parsing a URL variation config ({{parse-a-url-variation-config}}) given _fieldValue_. (((parse a URL variation config)))

### Examples

The following illustrates how various inputs are parsed, in terms of their impact on the resulting no-vary params and vary params:

| Input                                  | Result                                                                                |
|----------------------------------------+---------------------------------------------------------------------------------------|
| `No-Vary-Search: key-order`            | no-vary params: (empty list)<br>vary params: __wildcard__<br>vary on key order: false |
| `No-Vary-Search: params=("a")`         | no-vary params: « "`a`" »<br>vary params: __wildcard__                                |
| `No-Vary-Search: except=("x")`         | no-vary params: __wildcard__<br>vary params: « "`x`" »                                |
| `No-Vary-Search: params=()`            | no-vary params: (empty list)<br>vary params: __wildcard__                             |
| `No-Vary-Search: except=()`            | no-vary params: __wildcard__<br>vary params: (empty list)                             |

The following inputs are all invalid and will cause the default URL variation config to be returned:

| Input                                        | Explanation                                         |
|----------------------------------------------|-----------------------------------------------------|
| `No-Vary-Search: key-order="not a boolean"`  | `key-order` expects a boolean, not a string         |
| `No-Vary-Search: params="not an inner list"` | `params` expects an inner list, not a string        |
| `No-Vary-Search: params=(not-a-string)`      | `params` items must be strings (tokens are invalid) |
| `No-Vary-Search: params=?0`                  | `params` expects an inner list, not a boolean       |
| `No-Vary-Search: params=?1`                  | `params` expects an inner list, not a boolean       |
| `No-Vary-Search: params=?1, except=("x")`    | `params` and `except` cannot both be present        |
| `No-Vary-Search: params=("a"), except=("x")` | `params` and `except` cannot both be present        |
| `No-Vary-Search: params=(), except=()`       | `params` and `except` cannot both be present        |
| `No-Vary-Search: except="not an inner list"` | `except` expects an inner list, not a string        |
| `No-Vary-Search: except=(not-a-string)`      | `except` items must be strings (tokens are invalid) |
| `No-Vary-Search: except=?1`                  | `except` expects an inner list, not a boolean       |

  The following inputs are valid, but somewhat unconventional. They are shown alongside their more conventional form.

| Input                                             | Conventional form                                 |
|---------------------------------------------------+---------------------------------------------------|
| `No-Vary-Search: key-order=?1`                    | `No-Vary-Search: key-order`                       |
| `No-Vary-Search: except=("x")`, key-order         | `No-Vary-Search: key-order, except=("x")`         |
| `No-Vary-Search: params=()`                       | (omit the header field)                           |
| `No-Vary-Search: key-order=?0`                    | (omit the header field)                           |

## Parse a key {#parse-a-key}

*[parse a key]: #parse-a-key

(((!parse a key)))
To _parse a key_ given an ASCII string _keyString_:

  1. Let _keyBytes_ be the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _keyString_.

  1. Replace any 0x2B (+) in _keyBytes_ with 0x20 (SP).

  1. Let _keyBytesDecoded_ be the [percent-decoding](https://url.spec.whatwg.org/#percent-decode) {{WHATWG-URL}} of _keyBytes_.

  1. Let _keyStringDecoded_ be the [UTF-8 decoding without BOM](https://encoding.spec.whatwg.org/#utf-8-decode-without-bom) {{WHATWG-ENCODING}} of _keyBytesDecoded_.

  1. Return _keyStringDecoded_.

### Examples

The parse a key algorithm allows encoding non-ASCII key strings in the ASCII structured header field format, similar to how the [application/x-www-form-urlencoded](https://url.spec.whatwg.org/#concept-urlencoded) format {{WHATWG-URL}} allows encoding an entire entry list of keys and values in a URI (which is restricted to ASCII characters). For example:

~~~~http-message
No-Vary-Search: params=("%C3%A9+%E6%B0%97")
~~~~

Notice that while the input string `"%C3%A9+%E6%B0%97"` consists entirely of ASCII characters (as required at the HTTP layer), the percent-decoding step used by the cache produces a non-ASCII result. This will result in a URL variation config whose no-vary params are « "`é 気`" ». Note that the "`+`" character in the encoded string is mapped to a space (SP). As explained in a later example, the canonicalization process during equivalence testing means this will treat as equivalent URIs such as:

<!-- link "a later example" and "equivalence testing" -->

* `https://example.com/?é 気=1`
* `https://example.com/?é+気=2`
* `https://example.com/?%C3%A9%20気=3`
* `https://example.com/?%C3%A9+%E6%B0%97=4`

and so on, since they all are [parsed](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} to having the same key "`é 気`".

# Comparing {#comparing}

(((!equivalent modulo variation config)))
Two [URLs](https://url.spec.whatwg.org/#concept-url) {{WHATWG-URL}} _urlA_ and _urlB_ are _equivalent modulo variation config_ given a URL variation config _variationConfig_ if the following algorithm returns true:

1. If the scheme, host, port, or path of _urlA_ and _urlB_ differ, then return false.

1. If _variationConfig_ is equivalent to the default URL variation config, then:

    1. If _urlA_'s query equals _urlB_'s query, then return true.

    1. Return false.

    In this case, even URL pairs that might appear the same after running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} on their queries, such as `https://example.com/a` and `https://example.com/a?`, or `https://example.com/foo?a=b&&&c` and `https://example.com/foo?a=b&c=`, will be treated as inequivalent.

1. Let _searchParamsA_ and _searchParamsB_ be empty lists.

1. If _urlA_'s query is not null, then set _searchParamsA_ to the result of running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} given the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _urlA_'s query.

1. If _urlB_'s query is not null, then set _searchParamsB_ to the result of running the [application/x-www-form-urlencoded parser](https://url.spec.whatwg.org/#concept-urlencoded-parser) {{WHATWG-URL}} given the [isomorphic encoding](https://infra.spec.whatwg.org/#isomorphic-encode) {{WHATWG-INFRA}} of _urlB_'s query.

1. If _variationConfig_'s no-vary params is a list, then:

    1. Set _searchParamsA_ to a list containing those items _pair_ in _searchParamsA_ where _variationConfig_'s no-vary params does not contain _pair_\[0].

    1. Set _searchParamsB_ to a list containing those items _pair_ in _searchParamsB_ where _variationConfig_'s no-vary params does not contain _pair_\[0].

1. Otherwise, if _variationConfig_'s vary params is a list, then:

    1. Set _searchParamsA_ to a list containing those items _pair_ in _searchParamsA_ where _variationConfig_'s vary params contains _pair_\[0].

    1. Set _searchParamsB_ to a list containing those items _pair_ in _searchParamsB_ where _variationConfig_'s vary params contains _pair_\[0].

1. If _variationConfig_'s vary on key order is false, then:

    1. Let _keyLessThan_ be an algorithm taking as inputs two pairs (_keyA_, _valueA_) and (_keyB_, _valueB_), which returns whether _keyA_ is [code unit less than](https://infra.spec.whatwg.org/#code-unit-less-than) {{WHATWG-INFRA}} _keyB_.

    1. Set _searchParamsA_ to the result of [sorting](https://infra.spec.whatwg.org/#list-sort-in-ascending-order) {{WHATWG-INFRA}} _searchParamsA_ in ascending order with _keyLessThan_.

    1. Set _searchParamsB_ to the result of [sorting](https://infra.spec.whatwg.org/#list-sort-in-ascending-order) {{WHATWG-INFRA}} _searchParamsB_ in ascending order with _keyLessThan_.

1. If _searchParamsA_'s size is not equal to _searchParamsB_'s size, then return false.

1. Let _i_ be 0.

1. While _i_ < _searchParamsA_'s size:

    1. If _searchParamsA_\[_i_]\[0] does not equal _searchParamsB_\[_i_]\[0], then return false.

    1. If _searchParamsA_\[_i_]\[1] does not equal _searchParamsB_\[_i_]\[1], then return false.

    1. Set _i_ to _i_ + 1.

1. Return true.

## Examples

Due to how the application/x-www-form-urlencoded parser canonicalizes query strings, there are some cases where query strings which do not appear obviously equivalent, will end up being treated as equivalent after parsing.

So, for example, given any non-default value for the `"No-Vary-Search"` response header field, such as `No-Vary-Search: key-order`, we will have the following equivalences:

| First Query | Second Query    | Explanation                                         |
|-------------+-----------------+-----------------------------------------------------|
| null        | `?`             | A null query is parsed the same as an empty string  |
| `?a=x`      | `?%61=%78`      | Parsing performs percent-decoding                   |
| `?a=é`      | `?a=%C3%A9`     | Parsing performs percent-decoding                   |
| `?a=%f6`    | `?a=%ef%bf%bd`  | An invalid UTF-8 sequence and the literal U+FFFD character are both parsed as U+FFFD (&#xfffd;) |
| `?a=x&&&&`  | `?a=x`          | Parsing splits on `&` and discards empty strings    |
| `?a=`       | `?a`            | Both parse as having an empty string value for `a`  |
| `?a=%20`    | `?a= &`         | `%20` is parsed as U+0020 SPACE                     |
| `?a=+`      | `?a= &`         | `+` is parsed as U+0020 SPACE                       |

Note that no Unicode normalization is performed during this comparison. For example, a query string of `?a=%C3%A9` (using the NFC encoding of `é`) and `?a=e%CC%81` (using the NFD encoding of `é`) will not be treated as equivalent.

# Caching {#caching}

To reuse a stored response, {{Section 4 of HTTP-CACHING}} requires that the presented target URI and that of the stored response match. If a cache implements the `No-Vary-Search` extension, this matching requirement is also satisfied if the URIs are equivalent modulo URL variation config ({{comparing}}) given the stored response's `No-Vary-Search` header.

This document does not alter the requirements for cache invalidation (see Section 4.4 of {{HTTP-CACHING}}). A cache MAY invalidate stored responses for URIs that are equivalent modulo URL variation config, but is not required to do so. Therefore, state-changing requests might not invalidate all conceptually equivalent responses.

Note that the `"No-Vary-Search"` response header field operates in addition to content negotiation and the `Vary` header field (see Section 4.1 of {{HTTP-CACHING}}).

Cache implementations MAY fail to reuse a stored response whose target URI matches _only_ modulo URL variation config, if the cache has a stored response with a more recent `Date` header field which:

* has a target URI which is equal to the presented target URI, excluding the query, and
* has a non-empty value for the `"No-Vary-Search"` response header field, and
* has a `"No-Vary-Search"` response header field value different from the stored response being considered for reuse.

When a cache has multiple stored responses with conflicting `"No-Vary-Search"` values, preferring the response with the most recent `Date` header field helps ensure caches converge on the origin's latest caching policy.

{:aside}
> Caches aren't required to reuse stored responses, generally. However, the above expressly empowers caches to, if it is advantageous for performance or other reasons, search a smaller number of stored responses.
>
> That is, because caches might store more than one response for a given target URI path and authority, they need a way to efficiently look up the `"No-Vary-Search"` response header field value without accessing all cached responses. Such a cache might take steps like the following to identify a stored response in a performant way, before checking the other conditions in {{Section 4 of HTTP-CACHING}}:
>
> 1. Let exactMatch be cache\[presentedTargetURI\]. If it is a stored response that can be reused, return it.
> 1. Let targetPath be presentedTargetURI, with query parameters removed.
> 1. Let lastNVS be mostRecentNVS\[targetPath\]. If it does not exist, return null.
> 1. Let simplifiedURL be the result of simplifying presentedTargetURI according to lastNVS (by removing query parameters which are not significant, and [sorting](https://infra.spec.whatwg.org/#list-sort-in-ascending-order) {{WHATWG-INFRA}} parameters in ascending order by key, if key order is to be ignored).
> 1. Let nvsMatch be cache\[simplifiedURL\]. If it does not exist, return null. (It is assumed that this was written when storing in the cache, in addition to the exact URL.)
> 1. Let variationConfig be obtained ({{obtain-a-url-variation-config}}) from nvsMatch.
> 1. If nvsMatch's target URI and presentedTargetURI are not equivalent modulo URL variation config ({{comparing}}) given variationConfig, then return null.
> 1. If nvsMatch is a stored response that can be reused, return it. Otherwise, return null.

To aid cache implementation efficiency, servers SHOULD NOT send different non-empty values for the `"No-Vary-Search"` response header field in response to requests for a given target URI path and authority over time, unless there is a need to update how they handle the query component. Doing so would cause cache implementations that use a strategy like the above to miss some stored responses that could otherwise have been reused.

# Security Considerations

The main risk to be aware of is a cache returning a response that was originally fetched from a URL different from the one requested. In a web browser, this could cause the user to see a response fetched from a URL different from the one displayed when they hovered a link, or the URL displayed in the URL bar.

For shared caches, such as CDNs or forward proxies, returning a response for a different URL carries the risk of cross-user state leakage. If a server incorrectly declares that a query parameter does not affect the response, but that parameter actually dictates user-specific or sensitive content, the shared cache might serve one user's personalized response to another user. However, because the origin strictly controls the `"No-Vary-Search"` response header field, it is the origin's responsibility to ensure that ignored parameters are safe to disregard for all users.

The `"No-Vary-Search"` response header field alters the algorithm that caches use for URI identifier comparison. As discussed in {{?RFC6943}}, altering identifier comparison logic can lead to security issues, primarily through "false positives" where two identifiers are incorrectly deemed equivalent.

Because URL query parsing replaces invalid percent-encoded UTF-8 sequences with `U+FFFD`, lossy decoding can map distinct query strings onto the same cache key (for example, `?a=%f6` and `?a=%ef%bf%bd`). Origins should not rely on invalid percent-encoded sequences being distinguishable, as this is a concrete example of the false positives warned about in {{?RFC6943}}.

Incorrect configuration of this field can exacerbate cache poisoning or data leakage risks by causing such false positives. Origin servers MUST NOT declare a parameter as no-vary if doing so would bypass server processing required for safe response reuse. This includes parameters used for authorization, user identification, signature verification, user consent, routing, auditing, revocation, or any other security-sensitive operations.

However, since the impact is limited to query parameters, this does not cross the relevant security boundary, which is the origin ({{ORIGIN}}). (See also the [host](https://url.spec.whatwg.org/#concept-url-host) from [the perspective of web browser security UI](https://url.spec.whatwg.org/#url-rendering-simplification) {{WHATWG-URL}}). Indeed, origins already have complete control over how they present URLs and response bodies, including on the client side via technology such as [history.replaceState()](https://html.spec.whatwg.org/multipage/nav-history-apis.html#dom-history-replacestate) {{HTML}} or service workers.

# Privacy Considerations

This proposal is adjacent to the highly-privacy-relevant space of [navigational tracking](https://privacycg.github.io/nav-tracking-mitigations/#terminology), which often uses query parameters to pass along user identifiers. If an origin were to encode user identifiers in its URI, this proposal can reduce user tracking by private caches, since preventing server processing of such user IDs bypasses the server in favor of the cache. It does not interfere with [existing navigational tracking mitigations](https://privacycg.github.io/nav-tracking-mitigations/#deployed-mitigations), or any known future ones being contemplated. {{NAV-TRACKING-MITIGATIONS}}

However, this tracking reduction does not fully apply to shared caches (such as content delivery networks and forward proxies), which still receive the requests containing the identifiers. Furthermore, an errant configuration that incorrectly ignores parameters related to user identity or private state could expose cached content meant for one user to another. While this mistake can occur with standard caching, the `"No-Vary-Search"` response header field increases the surface area for such misconfigurations, making it critical that origins accurately classify their query parameters.

# IANA Considerations


## HTTP Field Names

IANA is requested to enter the following into the Hypertext Transfer Protocol (HTTP) Field Name Registry (<https://www.iana.org/assignments/http-fields/http-fields.xhtml>):

Field Name:
: `No-Vary-Search`

Status:
: permanent

Structured Type:
: Dictionary

Reference:
: this document

Comments:
: (none)

## No-Vary-Search Dictionary Keys Registry

IANA is requested to create a new registry, "No-Vary-Search Dictionary Keys", at <https://www.iana.org/assignments/http-fields/>.

The registration policy is "IETF Review" (see Section 4.8 of {{?RFC8126}}).

A registration request MUST include the following fields:

* Key: the dictionary key for the `"No-Vary-Search"` response header field
* Description: a brief description of the key's purpose
* Reference: a pointer to the specification that defines the key

The initial contents of this registry are:

| Key         | Description                                           | Reference     |
| ----------- | ----------------------------------------------------- | ------------- |
| `key-order` | Indicates if query parameter order affects caching    | this document |
| `params`    | A list of query parameters that do not affect caching | this document |
| `except`    | A list of query parameters that affect caching        | this document |

--- back

# Acknowledgments
{:numbered="false"}

This document benefited from valuable reviews and suggestions by:

* Adam Rice
* Julian Reschke
* Kevin McNee
* Liviu Tinta
* Mark Nottingham
* Martin Thomson
* Valentin Gosu
