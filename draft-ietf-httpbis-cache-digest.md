---
title: Cache Digests for HTTP/2
docname: draft-ietf-httpbis-cache-digest-latest
date: 2017
category: exp

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft

stand_alone: yes
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline]

author:
 -
    ins: K. Oku
    name: Kazuho Oku
    organization: DeNA Co, Ltd.
    email: kazuhooku@gmail.com

 -
    ins: M. Nottingham
    name: Mark Nottingham
    organization: 
    email: mnot@mnot.net
    uri: https://www.mnot.net/

normative:
  RFC2119:
  RFC3986:
  RFC6234:
  RFC6454:
  RFC7230:
  RFC7232:
  RFC7234:
  RFC7540:

informative:
  RFC4648:
  RFC5234:
  RFC6265:
  Rice:
    title: Adaptive variable-length coding for efficient compression of spacecraft television data
    author:
    -
      ins: R. F. Rice
      name: Robert F. Rice
    -
      ins: J. Plaunt
      name: James Plaunt
    date: December 1971
    seriesinfo:
      'IEEE Transactions on Communication Technology': 19.6
      DOI: 10.1109/TCOM.1971.1090789
      ISSN: 0018-9332 
  I-D.ietf-tls-tls13:
  Service-Workers:
    title: Service Workers 1
    author:
    - name: Alex Russell
    - name: Jungkee Song
    - name: Jake Archibald
    - name: Marijn Kruisselbrink
    date: 2016/10/11
    seriesinfo:
      'W3C Working Draft': WD-service-workers-1-20161011
    target: https://www.w3.org/TR/2016/WD-service-workers-1-20161011/
  Fetch:
    title: Fetch Standard
    target: https://fetch.spec.whatwg.org/
  Cuckoo:
    title: 'Cuckoo Filter: Practically Better Than Bloom'
    target: https://www.cs.cmu.edu/~dga/papers/cuckoo-conext2014.pdf

--- abstract

This specification defines a HTTP/2 frame type to allow clients to inform the server of their
cache's contents. Servers can then use this to inform their choices of what to push to clients.


--- note_Note_to_Readers

Discussion of this draft takes place on the HTTP working group mailing list 
(ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <http://httpwg.github.io/>; source 
code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/cache-digest>.

--- middle

# Introduction

HTTP/2 {{RFC7540}} allows a server to "push" synthetic request/response pairs into a client's cache
optimistically. While there is strong interest in using this facility to improve perceived Web
browsing performance, it is sometimes counterproductive because the client might already have
cached the "pushed" response.

When this is the case, the bandwidth used to "push" the response is effectively wasted, and
represents opportunity cost, because it could be used by other, more relevant responses. HTTP/2
allows a stream to be cancelled by a client using a RST_STREAM frame in this situation, but there
is still at least one round trip of potentially wasted capacity even then.

This specification defines a HTTP/2 frame type to allow clients to inform the server of their
cache's contents using a Cuckoo-fliter {{Cuckoo}} based digest. Servers can then use this to inform their
choices of what to push to clients.

## Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
{{RFC2119}}.


# The CACHE_DIGEST Frame

The CACHE_DIGEST frame type is 0xd (decimal 13).

~~~~
+-------------------------------+-------------------------------+
|         Origin-Len (16)       | Origin? (\*)                ...
+-------------------------------+-------------------------------+
|                   Digest-Value? (\*)                        ...
+---------------------------------------------------------------+
~~~~

The CACHE_DIGEST frame payload has the following fields:

Origin-Len:
: An unsigned, 16-bit integer indicating the length, in octets, of the Origin field.

Origin:
: A sequence of characters containing the ASCII serialization of an origin ({{!RFC6454}}, Section 6.2) that the Digest-Value applies to.

Digest-Value:
: A sequence of octets containing the digest as computed in {{creating}} and {{adding}}.

The CACHE_DIGEST frame defines the following flags:

* **RESET** (0x1): When set, indicates that any and all cache digests for the applicable origin held by the recipient MUST be considered invalid.

* **COMPLETE** (0x2): When set, indicates that the currently valid set of cache digests held by the server constitutes a complete representation of the cache's state regarding that origin, for the type of cached response indicated by the `STALE` flag.

## Client Behavior

A CACHE_DIGEST frame MUST be sent from a client to a server on stream 0, and conveys a digest of
the contents of the client's cache for the indicated origin.

In typical use, a client will send one or more CACHE_DIGESTs immediately after the first request on
a connection for a given origin, on the same stream, because there is usually a short period of
inactivity then, and servers can benefit most when they understand the state of the cache before
they begin pushing associated assets (e.g., CSS, JavaScript and images). Clients MAY send
CACHE_DIGEST at other times.

If the cache's state is cleared, lost, or the client otherwise wishes the server to stop using
previously sent CACHE_DIGESTs, it can send a CACHE_DIGEST with the RESET flag set.

When generating CACHE_DIGEST, a client MUST NOT include cached responses whose URLs do not share
origins {{RFC6454}} with the indicated origin. Clients MUST NOT send CACHE_DIGEST frames on
connections that are not authoritative (as defined in {{RFC7540}}, 10.1) for the indicated origin.

Clients can choose to only send a subset of the suitable stored responses. However, when the
CACHE_DIGEST frames sent represent the complete set of stored responses of a given type, the last
such frame SHOULD have a COMPLETE flag set, to indicate to the server that it has all relevant
state of that type. Note that for the purposes of COMPLETE, responses cached since the beginning
of the connection or the last RESET flag on a CACHE_DIGEST frame need not be included.

CACHE_DIGEST will also include the cached responses' ETags, if they were present in the response.
This information can be used by servers to decide if a response needs to be pushed to clients;
If a response is cached and was not changed at the origin server, the server calculating its hash
will find it in the digest and therefore will not push it. If a response is cached but was
modified at the origin server, the server calculating its hash will not find it in the digest, so
the response will be pushed.

CACHE_DIGEST has no defined meaning when sent from servers, and SHOULD be ignored by clients.


### Creating a digest {#creating}
Given the following inputs:
* `P`, an integer smaller than 256, that indicates the probability of a false positive that is acceptable, expressed as `1/2\*\*P`.
* `N`, an integer that represents the number of entries - a prime number smaller than 2\*\*32

1. Let `f` be the number of bits per fingerprint, calculated as `P + 3`
2. Let `b` be the bucket size, defined as 4.
3. Let `bytes` be `f`*`N`*`b`/8 rounded up to the nearest integer
4. Add 5 to `bytes`
5. Allocate memory of `bytes` and set it to zero. Assign it to `digest-value`.
6. Set the first byte to `P`
7. Set the second till fifth bytes to `N` in big endian form
8. Return the `digest-value`.

### Adding a URL to the Digest-Value {#adding}

Given the following inputs:

* `URL` a string corresponding to the Effective Request URI ({{RFC7230}}, Section 5.5) of a cached response {{RFC7234}}
* `ETag` a string corresponding to the entity-tag {{RFC7232}} if a cached response {{RFC7234}} (if the ETag is available; otherwise, null);
* `maxcount` - max number of cuckoo hops
* `digest-value`

1. Let `f` be the value of the first byte of `digest-value`.
2. Let `b` be the bucket size, defined as 4.
3. Let `N` be the value of the second to fifth bytes of `digest-value` in big endian form.
4. Let `key` be the return value of {{key}} with `URL` and `ETag` as inputs.
5. Let `h1` be the return value of {{hash}} with `key` and `N` as inputs.
6. Let `fingerprint` be the return value of {{fingerprint}} with `key`, `N` and `f` as inputs.
7. Let `h2` be the return value of {{hash}} with `fingerprint` and `N` as inputs, XORed with `h1`.
8. Let `h` be either `h1` or `h2`, picked in random.
9. Let `position_start` be 40 + `h` * `f`.
10. Let `position_end` be `position_start` + `f` * `b`.
11. While `position_start` < `position_end`:
    1. Let `bits` be `f` bits from `digest_value` starting at `position_start`.
    2. If `bits` is all zeros, set `bits` to `fingerprint` and terminate these steps.
    3. Add `f` to `position_start`.
12. Substract `f` from `position_start`.
13. Let `fingerprint` be the `f` bits starting at `position_start`.
14. Let `h1` be `h`
15. Substract 1 from `maxcount`.
16. If `maxcount` is zero, return an error.
17. Go to step 7.


### Removing a URL to the Digest-Value {#removing}

Given the following inputs:

* `URL` a string corresponding to the Effective Request URI ({{RFC7230}}, Section 5.5) of a cached response {{RFC7234}}
* `ETag` a string corresponding to the entity-tag {{RFC7232}} if a cached response {{RFC7234}} (if the ETag is available; otherwise, null);
* `digest-value`

1. Let `f` be the value of the first byte of `digest-value`.
2. Let `b` be the bucket size, defined as 4.
3. Let `N` be the value of the second to fifth bytes of `digest-value` in big endian form.
4. Let `key` be the return value of {{key}} with `URL` and `ETag` as inputs.
5. Let `h1` be the return value of {{hash}} with `key` and `N` as inputs.
6. Let `fingerprint` be the return value of {{fingerprint}} with `key`, `N` and `f` as inputs.
7. Let `h2` be the return value of {{hash}} with `fingerprint` and `N` as inputs, XORed with `h1`.
8. Let `h` be `h1`.
9. Let `position_start` be 40 + `h` * `f`.
10. Let `position_end` be `position_start` + `f` * `b`.
11. While `position_start` < `position_end`:
    1. Let `bits` be `f` bits from `digest_value` starting at `position_start`.
    2. If `bits` is `fingerprint`, set `bits` to all zeros and terminate these steps.
    3. Add `f` to `position_start`.
12. If `h` is not `h2`, set `h` to `h2` and return to step 9.

### Computing a fingerprint value {#fingerprint}

Given the following inputs:

* `key`, an array of characters
* `N`, an integer
* `f`, an integer indicating the number of output bits

1. Let `hash-value` be the return value of {{hash}} with `key` and `N` as inputs.
2. Let `h` be the number of bits in `hash-value`
3. Let `fingerprint-value` be 0
4. While `fingerprint-value` is 0 and `h` > `f`:
    4.1. Let `fingerprint-value` be the `f` least significant bits of `hash-value`.
    4.2. Let `hash-value` be the the `h`-`f` most significant bits of `hash-value`.
    4.3. `h` -= `f`
5. If `fingerprint-value` is 0, let `fingerprint-value` be 1.
6. Return `fingerprint-value`.

Note: Step 5 is to handle the extremely unlikely case where a SHA-256 digest of `key` is all zeros. The implications of it means that
there's an infitisimaly larger probability of getting a `fingerprint-value` of 1 compared to all other values. This is not a problem for any
practical purpose.



### Computing the key {#key}

Given the following inputs:

* `URL`, an array of characters
* `ETag`, an array of characters

1. Let `key` be `URL` converted to an ASCII string by percent-encoding as appropriate {{RFC3986}}.
2. If `ETag` is not null:
   1. Append `ETag` to `key` as an ASCII string, including both the `weak` indicator (if present) and double quotes, as per {{RFC7232}}, Section 2.3.
3. Return `key`

### Computing a Hash Value {#hash}

Given the following inputs:

* `key`, an array of characters.
* `N`, an integer

`hash-value` can be computed using the following algorithm:

1. Let `hash-value` be the SHA-256 message digest {{RFC6234}} of `key`, expressed as an integer.
2. Return `hash-value` modulo N.


## Server Behavior

In typical use, a server will query (as per {{querying}}) the CACHE_DIGESTs received on a given
connection to inform what it pushes to that client;

 * If a given URL and ETag combination has a match in a current CACHE_DIGEST, a complete response need not be pushed; The server MAY push a
 304 response for that resource, indicating the client that it hasn't changed.
 * If a given URL and ETag has no match in any current CACHE_DIGEST, the client does not have a cached copy, and a complete response can be pushed.

Servers MAY use all CACHE_DIGESTs received for a given origin as current, as long as they do not
have the RESET flag set; a CACHE_DIGEST frame with the RESET flag set MUST clear any
previously stored CACHE_DIGESTs for its origin. Servers MUST treat an empty Digest-Value with a
RESET flag set as effectively clearing all stored digests for that origin.

Clients are not likely to send updates to CACHE_DIGEST over the lifetime of a connection; it is
expected that servers will separately track what cacheable responses have been sent previously on
the same connection, using that knowledge in conjunction with that provided by CACHE_DIGEST.

Servers MUST ignore CACHE_DIGEST frames sent on a stream other than 0.


### Querying the Digest for a Value {#querying}

Given the following inputs:

* `URL` a string corresponding to the Effective Request URI ({{RFC7230}}, Section 5.5) of a cached response {{RFC7234}}.
* `ETag` a string corresponding to the entity-tag {{RFC7232}} if a cached response {{RFC7234}} (if the ETag is available; otherwise, null).
* `digest-value`, an array of bits.

1. Let `f` be the value of the first byte of `digest-value`.
2. Let `b` be the bucket size, defined as 4.
3. Let `N` be the value of the second to fifth bytes of `digest-value` in big endian form.
4. Let `key` be the return value of {{key}} with `URL` and `ETag` as inputs.
5. Let `h1` be the return value of {{hash}} with `key` and `N` as inputs.
6. Let `fingerprint` be the return value of {{fingerprint}} with `key`, `N` and `f` as inputs.
7. Let `h2` be the return value of {{hash}} with `fingerprint` and `N` as inputs, XORed with `h1`.
8. Let `h` be `h1`.
9. Let `position_start` be 40 + `h` * `f`.
10. Let `position_end` be `position_start` + `f` * `b`.
11. While `position_start` < `position_end`:
    1. Let `bits` be `f` bits from `digest_value` starting at `position_start`.
    2. If `bits` is `fingerprint`, return true
    3. Add `f` to `position_start`.
12. Return false.

# The SENDING_CACHE_DIGEST SETTINGS Parameter

A Client SHOULD notify its support for CACHE_DIGEST frames by sending the SENDING_CACHE_DIGEST (0xXXX) SETTINGS parameter.

The value of the parameter is a bit-field of which the following bits are defined:

DIGEST_PENDING (0x1): When set it indicates that the client has a digest to send, and the server may choose to wait for a digest in order to make
server push decisions.

Rest of the bits MUST be ignored and MUST be left unset when sending.

The initial value of the parameter is zero (0x0) meaning that the client has no digest to send the server.

# The ACCEPT_CACHE_DIGEST SETTINGS Parameter

A server can notify its support for CACHE_DIGEST frame by sending the ACCEPT_CACHE_DIGEST (0x7) SETTINGS parameter.
If the server is tempted to making optimizations based on CACHE_DIGEST frames, it SHOULD send the SETTINGS parameter immediately after the connection is established.

The value of the parameter is a bit-field of which the following bits are defined:

ACCEPT (0x1): When set, it indicates that the server is willing to make use of a digest of cached responses.

Rest of the bits MUST be ignored and MUST be left unset when sending.

The initial value of the parameter is zero (0x0) meaning that the server is not interested in seeing a CACHE_DIGEST frame.

Some underlying transports allow the server's first flight of application data to reach the client at around the same time when the client sends it's first flight data. When such transport (e.g., TLS 1.3 {{I-D.ietf-tls-tls13}} in full-handshake mode) is used, a client can postpone sending the CACHE_DIGEST frame until it receives a ACCEPT_CACHE_DIGEST settings value.

When the underlying transport does not have such property (e.g., TLS 1.3 in 0-RTT mode), a client can reuse the settings value found in previous connections to that origin {{RFC6454}} to make assumptions.

# IANA Considerations

This document registers the following entry in the Permanent Message Headers Registry, as per {{?RFC3864}}:

* Header field name: Cache-Digest
* Applicable protocol: http
* Status: experimental
* Author/Change controller: IESG
* Specification document(s): [this document]

This document registers the following entry in the HTTP/2 Frame Type Registry, as per {{RFC7540}}:

* Frame Type: CACHE_DIGEST
* Code: 0xd
* Specification: [this document]

This document registers the following entry in the HTTP/2 Settings Registry, as per {{RFC7540}}:

* Code: 0x7
* Name: ACCEPT_CACHE_DIGEST
* Initial Value: 0x0
* Reference: [this document]

# Security Considerations

The contents of a User Agent's cache can be used to re-identify or "fingerprint" the user over
time, even when other identifiers (e.g., Cookies {{RFC6265}}) are cleared. 

CACHE_DIGEST allows such cache-based fingerprinting to become passive, since it allows the server
to discover the state of the client's cache without any visible change in server behaviour.

As a result, clients MUST mitigate for this threat when the user attempts to remove identifiers
(e.g., "clearing cookies"). This could be achieved in a number of ways; for example: by clearing
the cache, by changing one or both of N and P, or by adding new, synthetic entries to the digest to
change its contents.

TODO: discuss how effective the suggested mitigations actually would be.

Additionally, User Agents SHOULD NOT send CACHE_DIGEST when in "privacy mode."


--- back

# Encoding the CACHE_DIGEST frame as an HTTP Header

On some web browsers that support Service Workers {{Service-Workers}} but not Cache Digests (yet), it is possible to achieve the benefit of using Cache Digests by emulating the frame using HTTP Headers.

For the sake of interoperability with such clients, this appendix defines how a CACHE_DIGEST frame can be encoded as an HTTP header named `Cache-Digest`.

The definition uses the Augmented Backus-Naur Form (ABNF) notation of {{RFC5234}} with the list rule extension defined in {{RFC7230}}, Section 7.

~~~ abnf7230
  Cache-Digest  = 1#digest-entity
  digest-entity = digest-value *(OWS ";" OWS digest-flag)
  digest-value  = <Digest-Value encoded using base64url>
  digest-flag   = token
~~~

A Cache-Digest request header is defined as a list construct of cache-digest-entities.
Each cache-digest-entity corresponds to a CACHE_DIGEST frame.

Digest-Value is encoded using base64url {{RFC4648}}, Section 5.
Flags that are set are encoded as digest-flags by their names that are compared case-insensitively.

Origin is omitted in the header form.
The value is implied from the value of the `:authority` pseudo header.
Client MUST only send Cache-Digest headers containing digests that belong to the origin specified by the HTTP request.

The example below contains one digest of fresh resource and has only the `COMPLETE` flag set.

~~~ example
  Cache-Digest: AfdA; complete
~~~

Clients MUST associate Cache-Digest headers to every HTTP request, since Fetch {{Fetch}} - the HTTP API supported by Service Workers - does not define the order in which the issued requests will be sent to the server nor guarantees that all the requests will be transmitted using a single HTTP/2 connection.

Also, due to the fact that any header that is supplied to Fetch is required to be end-to-end, there is an ambiguity in what a Cache-Digest header respresents when a request is transmitted through a proxy.
The header may represent the cache state of a client or that of a proxy, depending on how the proxy handles the header.

# Acknowledgements

Thanks to Adam Langley and Giovanni Bajo for their explorations of Golomb-coded sets. In
particular, see
<http://giovanni.bajo.it/post/47119962313/golomb-coded-sets-smaller-than-bloom-filters>, which
refers to sample code.

Thanks to Stefan Eissing for his suggestions.

# Changes

## Since draft-ietf-httpbis-cache-digest-02

* None yet.

## Since draft-ietf-httpbis-cache-digest-01

* Added definition of the Cache-Digest header.
* Introduce ACCEPT_CACHE_DIGEST SETTINGS parameter.
* Change intended status from Standard to Experimental.

## Since draft-ietf-httpbis-cache-digest-00

* Make the scope of a digest frame explicit and shift to stream 0.
