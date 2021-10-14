---
title: Targeted HTTP Cache Control
docname: draft-ietf-httpbis-targeted-cache-control-latest
date: {NOW}
category: std

ipr: trust200902
area: General
workgroup: HTTP
keyword:
 - CDN
 - Content Delivery Network
 - Caching

stand_alone: yes
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline]
github-issue-label: targeted-cc

author:
 -
    ins: S. Ludin
    name: Stephen Ludin
    organization: Akamai
    email: sludin@ludin.org
 -
    ins: M. Nottingham
    name: Mark Nottingham
    organization: Fastly
    postal:
      - Prahran
    country: Australia
    email: mnot@mnot.net
    uri: https://www.mnot.net/
 -
    ins: Y. Wu
    name: Yuchen Wu
    organization: Cloudflare
    email: me@yuchenwu.net

normative:
  RFC2119:
  HTTP: I-D.ietf-httpbis-semantics
  HTTP-CACHING: I-D.ietf-httpbis-cache
  STRUCTURED-FIELDS: RFC8941

informative:
  AGE-PENALTY:
    target: https://dl.acm.org/doi/10.5555/1251440.1251447
    title: The age penalty and its effect on cache performance
    date: March 2001
    author:
     -
        ins: E. Cohen
        name: Edith Cohen
        organization: "AT&T Labs - Research"
        email: edith@research.att.com
     -
        ins: H. Kaplan
        name: Haim Kaplan
        organization: School of Computer Science, Tel-Aviv University
        email: haimk@math.tau.ac.il


--- abstract

This specification defines a convention for HTTP response header fields that allow directives controlling caching to be targeted at specific caches or classes of caches. It also defines one such header field, targeted at Content Delivery Network (CDN) caches.

--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

The issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/targeted-cc>.

The most recent (often, unpublished) draft is at <https://httpwg.org/http-extensions/draft-ietf-httpbis-targeted-cache-control.html>.

See also the draft's current status in the IETF datatracker, at
<https://datatracker.ietf.org/doc/draft-ietf-httpbis-targeted-cache-control/>.

--- middle

# Introduction


Modern deployments of HTTP often use multiple layers of caching with varying properties. For example, a Web site might use a cache on the origin server itself; it might deploy a caching layer in the same network as the origin server, it might use one or more Content Delivery Networks (CDNs) that are distributed throughout the Internet, and it might utilise browser caching as well.

Because it is often desirable to control these different classes of caches separately, some means of targeting directives at them is necessary.

The HTTP Cache-Control response header field is widely used to direct caching behavior. However, it is relatively undifferentiated; while some directives (e.g., s-maxage) are targeted at a specific class of caches (for s-maxage, shared caches), targeting is not consistently available across all existing cache directives (e.g., stale-while-revalidate). This is problematic, especially as the number of caching extensions grows, along with the number of potential targets.

Some implementations have defined ad hoc control mechanisms to overcome this issue, but their interoperability is low. {{targeted}} defines a standard framework for targeted cache control using HTTP response headers, and {{cdn-cache-control}} defines one such header: the CDN-Cache-Control response header field.


## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as
described in BCP 14 {{!RFC2119}} {{!RFC8174}} when, and only when, they appear in all capitals, as
shown here.


# Targeted Cache-Control Header Fields {#targeted}

A Targeted Cache-Control Header Field (hereafter, "targeted field") is a HTTP response header field that has the same semantics as the Cache-Control response header field ({{HTTP-CACHING, Section 5.2}}). However, it has a distinct field name that indicates the target for its directives.

For example:

~~~ http-message
CDN-Cache-Control: max-age=60
~~~

is a targeted field that applies to Content Delivery Networks (CDNs), as defined in {{cdn-cache-control}}.


## Syntax

Targeted fields are Dictionary Structured Fields ({{Section 3.2 of STRUCTURED-FIELDS}}). Each member of the dictionary is a cache directive from the Hypertext Transfer Protocol (HTTP) Cache Directive Registry.

Because cache directives are not defined in terms of structured data types, it is necessary to map their values into the appropriate types. Typically, they are mapped into a Boolean ({{Section 3.3.6 of STRUCTURED-FIELDS}}) when the member has no separate value, a Token ({{Section 3.3.4 of STRUCTURED-FIELDS}}) for alphanumeric values, a String ({{Section 3.3.3 of STRUCTURED-FIELDS}}) for quote-delimited values, or an Integer ({{Section 3.3.1 of STRUCTURED-FIELDS}}) for purely numeric values.

For example, the max-age directive ({{Section 5.2.2.1 of HTTP-CACHING}}) has an integer value; no-store ({{Section 5.2.2.5 of HTTP-CACHING}}) always has a boolean true value, and no-cache ({{Section 5.2.2.4 of HTTP-CACHING}}) has a value that can either be boolean true or a string containing a comma-delimited list of field names.

Implementations MUST NOT generate and SHOULD NOT consume values that violate these inferred constraints on the directive's value (e.g. coerce a max-age with a decimal value into an integer). Parameters received on directives are to be ignored, unless other handling is explicitly specified.

If a targeted field in a given response is empty, or a parsing error is encountered, that field MUST be ignored by the cache (i.e., it behaves as if the field were not present, likely falling back to other cache control mechanisms present).


## Cache Behavior

A cache that implement this specification maintains a _target list_ - an ordered list of the targeted field names that it uses for caching policy, with the order reflecting priority from most applicable to least. The target list might be fixed, user-configurable, or generated per request, depending upon the implementation.

For example, a CDN cache might support both CDN-Cache-Control and a header specific to that CDN, ExampleCDN-Cache-Control, with the latter overriding the former. Its target list would be:

~~~
  [ExampleCDN-Cache-Control, CDN-Cache-Control]
~~~

When a cache that implements this specification receives a response with one or more of of the header field names on its target list, the cache MUST select the first (in target list order) field with a valid, non-empty value and use its value to determine the caching policy for the response, and MUST ignore the Cache-Control and Expires header fields in that response, unless no valid, non-empty value is available from the listed header fields.

Note that this occurs on a response-by-response basis; if no member of the cache's target list is present, valid and non-empty, a cache falls back to other cache control mechanisms as required by HTTP {{HTTP-CACHING}}.

Targeted fields that are not on a cache's target list MUST NOT change that cache's behaviour, and MUST be passed through.

Caches that use a targeted field MUST implement the semantics of the following cache directives:

* max-age
* must-revalidate
* no-store
* no-cache
* private

Furthermore, they SHOULD implement other cache directives (including extension cache directives) that they support in the Cache-Control response header field.

The semantics and precedence of cache directives in a targeted field are the same as those in Cache-Control. In particular, no-store and no-cache make max-age inoperative, and unrecognised extension directives are ignored.



## Interaction with HTTP Freshness

HTTP caching has a single, end-to-end freshness model defined in {{Section 4.2 of HTTP-CACHING}}. When additional freshness mechanisms are only available to some caches along a request path (for example, using targeted fields), their interactions need to be carefully considered. In particular, a targeted cache might have longer freshness lifetimes available to it than other caches, causing it to serve responses that appear to be prematurely (or even immediately) stale to them, negatively impacting cache efficiency.

For example, a response stored by a CDN cache might be served with the following headers:

~~~ http-message
Age: 1800
Cache-Control: max-age=600
CDN-Cache-Control: max-age=3600
~~~

From the CDN's perspective, this response is still fresh after being cached for 30 minutes, while from other caches' standpoint, this response is already stale. See {{AGE-PENALTY}} for more discussion.

When the targeted cache has a strong coherence mechanism (e.g., the origin server has the ability to proactively invalidate cached responses), it is often desirable to mitigate these effects. Some techniques seen in deployments include:

* Removing the Age header field
* Updating the Date header field value to the current time
* Updating the Expires header field value to the current time, plus any Cache-Control: max-age value

This specification does not place any specific requirements on implementations to mitigate these effects, but definitions of targeted fields can do so.


## Defining Targeted Fields

A targeted field for a particular class of cache can be defined by requesting registration in the Hypertext Transfer Protocol (HTTP) Field Name Registry <https://www.iana.org/assignments/http-fields/>, listing this specification as the specification document. The Comments field of the registration should clearly define the class of caches that the targeted field applies to.

By convention, targeted fields have the suffix "-Cache-Control": e.g., "ExampleCDN-Cache-Control". However, this suffix MUST NOT be used on its own to identify targeted fields; it is only a convention.


# The CDN-Cache-Control Targeted Field {#cdn-cache-control}

The CDN-Cache-Control response header field is a targeted field ({{targeted}}) that allows origin servers to control the behaviour of CDN caches interposed between them and clients, separately from other caches that might handle the response.

It applies to caches that are part of a distributed network that operate on behalf of an origin server (commonly called a Content Delivery Network or CDN).

CDN caches that use CDN-Cache-Control will typically forward this header so that downstream CDN caches can use it as well. However, they MAY remove it when this is undesirable (for example, when configured to do so because it is known not to be used downstream).


## Examples

For example, the following header fields would instruct a CDN cache to consider the response fresh for 600 seconds, other shared caches for 120 seconds and any remaining caches for 60 seconds:

~~~ http-message
Cache-Control: max-age=60, s-maxage=120
CDN-Cache-Control: max-age=600
~~~

These header fields would instruct a CDN cache to consider the response fresh for 600 seconds, while all other caches would be prevented from storing it:

~~~ http-message
CDN-Cache-Control: max-age=600
Cache-Control: no-store
~~~

Because CDN-Cache-Control is not present, this header field would prevent all caches from storing the response:

~~~ http-message
Cache-Control: no-store
~~~

Whereas these would prevent all caches except for CDN caches from storing the response:

~~~ http-message
Cache-Control: no-store
CDN-Cache-Control: none
~~~

(note that 'none' is not a registered cache directive; it is here to avoid sending a header field with an empty value, which would be ignored)


# IANA Considerations

Please register the following entry in the Hypertext Transfer Protocol (HTTP) Field Name Registry
defined by {{HTTP}}:

* Field Name: CDN-Cache-Control
* Status: permanent
* Specification Document: \[this document\]
* Comments: Cache-Control directives targeted at Content Delivery Networks


# Security Considerations

The security considerations of HTTP caching {{HTTP-CACHING}} apply.

The ability to carry multiple caching policies on a response can result in confusion about how a response will be cached in different systems, if not used carefully. This might result in unintentional reuse of responses with sensitive information.


--- back

