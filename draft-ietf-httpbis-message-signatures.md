---
title: HTTP Message Signatures
docname: draft-ietf-httpbis-message-signatures-latest
category: std

ipr: trust200902
area: Applications and Real-Time
workgroup: HTTP
keyword: Internet-Draft
keyword: HTTP
keyword: digital-signatures
keyword: PKI

stand_alone: yes
smart_quotes: no
pi: [toc, tocindent, sortrefs, symrefs, strict, compact, comments, inline, docmapping]

venue:
  group: HTTP
  type: Working Group
  home: https://httpwg.org/
  mail: ietf-http-wg@w3.org
  arch: https://lists.w3.org/Archives/Public/ietf-http-wg/
  repo: https://github.com/httpwg/http-extensions/labels/signatures
github-issue-label: signatures

author:
  - ins: A. Backman
    name: Annabelle Backman
    org: Amazon
    email: richanna@amazon.com
    uri: https://www.amazon.com/
    street: P.O. Box 81226
    city: Seattle
    region: WA
    code: 98108-1226
    country: United States of America
    role: editor

  - ins: J. Richer
    name: Justin Richer
    org: Bespoke Engineering
    email: ietf@justin.richer.org
    uri: https://bspk.io/

  - ins: M. Sporny
    name: Manu Sporny
    org: Digital Bazaar
    email: msporny@digitalbazaar.com
    uri: https://manu.sporny.org/
    street: 203 Roanoke Street W.
    city: Blacksburg
    region: VA
    code: 24060
    country: United States of America

normative:
    RFC2104:
    RFC3986:
    RFC6234:
    RFC7517:
    RFC7518:
    RFC8017:
    RFC8032:
    RFC8941:
    FIPS186-4:
        target: https://csrc.nist.gov/publications/detail/fips/186/4/final
        title: Digital Signature Standard (DSS)
        date: 2013
    POSIX.1:
        target: https://pubs.opengroup.org/onlinepubs/9699919799/
        title: The Open Group Base Specifications Issue 7, 2018 edition
        date: 2018
    SEMANTICS: I-D.ietf-httpbis-semantics
    MESSAGING: I-D.ietf-httpbis-messaging
    HTMLURL:
        target: https://url.spec.whatwg.org/
        title: URL (Living Standard)
        date: 2021

informative:
    RFC7239:
    BCP195:
    I-D.ietf-httpbis-client-cert-field:

--- abstract

This document describes a mechanism for creating, encoding, and verifying digital signatures or message authentication codes over components of an HTTP message.  This mechanism supports use cases where the full HTTP message may not be known to the signer, and where the message may be transformed (e.g., by intermediaries) before reaching the verifier.
This document also describes a means for requesting that a signature be applied to a subsequent HTTP message in an ongoing HTTP exchange.

--- middle

# Introduction {#intro}

Message integrity and authenticity are important security properties that are critical to the secure operation of many HTTP applications.
Application developers typically rely on the transport layer to provide these properties, by operating their application over {{?TLS=RFC8446}}.  However, TLS only guarantees these properties over a single TLS connection, and the path between client and application may be composed of multiple independent TLS connections (for example, if the application is hosted behind a TLS-terminating gateway or if the client is behind a TLS Inspection appliance).  In such cases, TLS cannot guarantee end-to-end message integrity or authenticity between the client and application.  Additionally, some operating environments present obstacles that make it impractical to use TLS, or to use features necessary to provide message authenticity.  Furthermore, some applications require the binding of an application-level key to the HTTP message, separate from any TLS certificates in use. Consequently, while TLS can meet message integrity and authenticity needs for many HTTP-based applications, it is not a universal solution.

This document defines a mechanism for providing end-to-end integrity and authenticity for components of an HTTP message.  The mechanism allows applications to create digital signatures or message authentication codes (MACs) over only the components of the message that are meaningful and appropriate for the application.  Strict canonicalization rules ensure that the verifier can verify the signature even if the message has been transformed in any of the many ways permitted by HTTP.

The signing mechanism described in this document consists of three parts:

- A common nomenclature and canonicalization rule set for the different protocol elements and other components of HTTP messages, used to create a signature input.
- Algorithms for generating and verifying signatures over HTTP message components using this signature input through application of cryptographic primitives.
- A mechanism for attaching a signature and related metadata to an HTTP message, and for parsing attached signatures and metadata from HTTP messages.

This document also provides a mechanism for a potential verifier to signal to a potential signer that a signature is desired in one or more subsequent messages. This optional negotiation mechanism can be used along with opportunistic or application-driven message signatures by either party.

## Requirements Discussion

HTTP permits and sometimes requires intermediaries to transform messages in a variety of ways.  This may result in a recipient receiving a message that is not bitwise equivalent to the message that was originally sent.  In such a case, the recipient will be unable to verify a signature over the raw bytes of the sender's HTTP message, as verifying digital signatures or MACs requires both signer and verifier to have the exact same signature input.  Since the exact raw bytes of the message cannot be relied upon as a reliable source of signature input, the signer and verifier must derive the signature input from their respective versions of the message, via a mechanism that is resilient to safe changes that do not alter the meaning of the message.

For a variety of reasons, it is impractical to strictly define what constitutes a safe change versus an unsafe one.  Applications use HTTP in a wide variety of ways, and may disagree on whether a particular piece of information in a message (e.g., the body, or the `Date` header field) is relevant.  Thus a general purpose solution must provide signers with some degree of control over which message components are signed.

HTTP applications may be running in environments that do not provide complete access to or control over HTTP messages (such as a web browser's JavaScript environment), or may be using libraries that abstract away the details of the protocol (such as [the Java HTTPClient library](https://openjdk.java.net/groups/net/httpclient/intro.html)).  These applications need to be able to generate and verify signatures despite incomplete knowledge of the HTTP message.

## HTTP Message Transformations {#transforms}

As mentioned earlier, HTTP explicitly permits and in some cases requires implementations to transform messages in a variety of ways.  Implementations are required to tolerate many of these transformations.  What follows is a non-normative and non-exhaustive list of transformations that may occur under HTTP, provided as context:

- Re-ordering of header fields with different header field names ({{Section 3.2.2 of MESSAGING}}).
- Combination of header fields with the same field name ({{Section 3.2.2 of MESSAGING}}).
- Removal of header fields listed in the `Connection` header field ({{Section 6.1 of MESSAGING}}).
- Addition of header fields that indicate control options ({{Section 6.1 of MESSAGING}}).
- Addition or removal of a transfer coding ({{Section 5.7.2 of MESSAGING}}).
- Addition of header fields such as `Via` ({{Section 5.7.1 of MESSAGING}}) and `Forwarded` ({{Section 4 of RFC7239}}).

## Safe Transformations

Based on the definition of HTTP and the requirements described above, we can identify certain types of transformations that should not prevent signature verification, even when performed on message components covered by the signature.  The following list describes those transformations:

- Combination of header fields with the same field name.
- Reordering of header fields with different names.
- Conversion between different versions of the HTTP protocol (e.g., HTTP/1.x to HTTP/2, or vice-versa).
- Changes in casing (e.g., "Origin" to "origin") of any case-insensitive components such as header field names, request URI scheme, or host.
- Addition or removal of leading or trailing whitespace to a header field value.
- Addition or removal of `obs-folds`.
- Changes to the `request-target` and `Host` header field that when applied together do not
  result in a change to the message's effective request URI, as defined in {{Section 5.5 of MESSAGING}}.

Additionally, all changes to components not covered by the signature are considered safe.


## Conventions and Terminology {#definitions}

{::boilerplate bcp14-tagged}

The terms "HTTP message", "HTTP request", "HTTP response",
`absolute-form`, `absolute-path`, "effective request URI",
"gateway", "header field", "intermediary", `request-target`,
"sender", and "recipient" are used as defined in {{MESSAGING}}.

The term "method" is to be interpreted as defined in {{Section 4 of SEMANTICS}}.

For brevity, the term "signature" on its own is used in this document to refer to both digital signatures (which use asymmetric cryptography) and keyed MACs (which use symmetric cryptography). Similarly, the verb "sign" refers to the generation of either a digital signature or keyed MAC over a given input string. The qualified term "digital signature" refers specifically to the output of an asymmetric cryptographic signing operation.

In addition to those listed above, this document uses the following terms:

{: vspace="0"}
HTTP Message Signature:
: A digital signature or keyed MAC that covers one or more portions of an HTTP message. Note that a given HTTP Message can contain multiple HTTP Message Signatures.

Signer:
: The entity that is generating or has generated an HTTP Message Signature. Note that multiple entities can act as signers and apply separate HTTP Message Signatures to a given HTTP Message.

Verifier:
: An entity that is verifying or has verified an HTTP Message Signature against an HTTP Message.  Note that an HTTP Message Signature may be verified multiple times, potentially by different entities.

HTTP Message Component:
: A portion of an HTTP message that is capable of being covered by an HTTP Message Signature.

HTTP Message Component Identifier:
: A value that uniquely identifies a specific HTTP Message Component in respect to a particular HTTP Message Signature and the HTTP Message it applies to.

HTTP Message Component Value:
: The value associated with a given component identifier within the context of a particular HTTP Message. Component values are derived from the HTTP Message and are usually subject to a canonicalization process.

Covered Components:
: An ordered set of HTTP message component identifiers for fields ({{http-header}}) and derived components ({{derived-components}}) that indicates the set of message components covered by the signature, never including the `@signature-params` identifier itself. The order of this set is preserved and communicated between the signer and verifier to facilitate reconstruction of the signature input.

Signature Input:
: The sequence of bytes processed by the cryptographic algorithm to produce or verify the HTTP Message Signature. The signature input is generated by the signer and verifier using the covered components set and the HTTP Message.

HTTP Message Signature Algorithm:
: A cryptographic algorithm that describes the signing and verification process for the signature, defined in terms of the `HTTP_SIGN` and `HTTP_VERIFY` primitives described in {{signature-methods}}.

Key Material:
: The key material required to create or verify the signature. The key material is often identified with an explicit key identifier, allowing the signer to indicate to the verifier which key was used.

Creation Time:
: A timestamp representing the point in time that the signature was generated, as asserted by the signer.

Expiration Time:
: A timestamp representing the point in time after which the signature should no longer be accepted by the verifier, as asserted by the signer.

The term "Unix time" is defined by {{POSIX.1}}, [Section 4.16](http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html#tag_04_16).

This document contains non-normative examples of partial and complete HTTP messages. Some examples use a single trailing backslash '\' to indicate line wrapping for long values, as per {{!RFC8792}}. The `\` character and leading spaces on wrapped lines are not part of the value.

## Application of HTTP Message Signatures {#application}

HTTP Message Signatures are designed to be a general-purpose security mechanism applicable in a wide variety of circumstances and applications. In order to properly and safely apply HTTP Message Signatures, an application or profile of this specification MUST specify all of the following items:

- The set of [component identifiers](#covered-content) that are expected and required. For example, an authorization protocol could mandate that the `Authorization` header be covered to protect the authorization credentials and mandate the signature parameters contain a `created` parameter, while an API expecting HTTP message bodies could require the `Digest` header to be present and covered.
- A means of retrieving the key material used to verify the signature. An application will usually use the `keyid` parameter of the signature parameters ({{signature-params}}) and define rules for resolving a key from there, though the appropriate key could be known from other means.
- A means of determining the signature algorithm used to verify the signature is appropriate for the key material. For example, the process could use the `alg` parameter of the signature parameters ({{signature-params}}) to state the algorithm explicitly, derive the algorithm from the key material, or use some pre-configured algorithm agreed upon by the signer and verifier.
- A means of determining that a given key and algorithm presented in the request are appropriate for the request being made. For example, a server expecting only ECDSA signatures should know to reject any RSA signatures, or a server expecting asymmetric cryptography should know to reject any symmetric cryptography.

An application using signatures also has to ensure that the verifier will have access to all required information to re-create the signature input string. For example, a server behind a reverse proxy would need to know the original request URI to make use of identifiers like `@target-uri`. Additionally, an application using signatures in responses would need to ensure that clients receiving signed responses have access to all the signed portions, including any portions of the request that were signed by the server.

The details of this kind of profiling are the purview of the application and outside the scope of this specification, however some additional considerations are discussed in {{security}}.

# HTTP Message Components {#covered-content}

In order to allow signers and verifiers to establish which components are covered by a signature, this document defines component identifiers for components covered by an HTTP Message Signature, a set of rules for deriving and canonicalizing the values associated with these component identifiers from the HTTP Message, and the means for combining these canonicalized values into a signature input string. The values for these items MUST be accessible to both the signer and the verifier of the message, which means these are usually derived from aspects of the HTTP message or signature itself.

Some HTTP message components can undergo transformations that change the bitwise value without altering meaning of the component's value (for example, the merging together of header fields with the same name).  Message component values must therefore be canonicalized before it is signed, to ensure that a signature can be verified despite such intermediary transformations. This document defines rules for each component identifier that transform the identifier's associated component value into such a canonical form.

Component identifiers are serialized using the production grammar defined by {{RFC8941, Section 4}}.
The component identifier itself is an `sf-string` value and MAY define parameters which are included using the `parameters` rule.

~~~ abnf
component-identifier = sf-string parameters
~~~

Note that this means the serialization of the component identifier itself is encased in double quotes, with parameters following as a semicolon-separated list, such as `"cache-control"`, `"date"`, or `"@signature-params"`.

Component identifiers, including component identifiers with parameters, MUST NOT be repeated within a single list of covered components. Component identifiers with different parameter values MAY be repeated within a single list of covered components.

The component value associated with a component identifier is defined by the identifier itself. Component values MUST NOT contain newline (`\n`) characters.

The following sections define component identifier types, their parameters, their associated values, and the canonicalization rules for their values. The method for combining component identifiers into the signature input is defined in {{create-sig-input}}.

## HTTP Fields {#http-header}

The component identifier for an HTTP field is the lowercased form of its field name. While HTTP field names are case-insensitive, implementations MUST use lowercased field names (e.g., `content-type`, `date`, `etag`) when using them as component identifiers.

Unless overridden by additional parameters and rules, the HTTP field value MUST be canonicalized as a single combined value as defined in {{Section 5.2 of SEMANTICS}}.

If the combined value is not available for a given header, the following algorithm will produce canonicalized results for an implementation:

1. Create an ordered list of the field values of each instance of the field in the message, in the order that they occur (or will occur) in the message.
2. Strip leading and trailing whitespace from each item in the list. Note that since HTTP field values are not allowed to contain leading and trailing whitespace, this will be a no-op in a compliant implementation.
3. Remove any obsolete line-folding within the line and replace it with a single space (" "), as discussed in {{Section 5.2 of MESSAGING}}. Note that this behavior is specific to {{MESSAGING}} and does not apply to other versions of the HTTP specification.
4. Concatenate the list of values together with a single comma (",") and a single space (" ") between each item.

The resulting string is the canonicalized component value.

Following are non-normative examples of canonicalized values for header fields, given the following example HTTP message fragment:

~~~ http-message
Host: www.example.com
Date: Tue, 20 Apr 2021 02:07:56 GMT
X-OWS-Header:   Leading and trailing whitespace.
X-Obs-Fold-Header: Obsolete
    line folding.
Cache-Control: max-age=60
Cache-Control:    must-revalidate
Example-Dict:  a=1,    b=2;x=1;y=2,   c=(a   b   c)
~~~

The following example shows canonicalized values for these example header fields, presented using the signature input string format discussed in {{create-sig-input}}:

~~~
"host": www.example.com
"date": Tue, 20 Apr 2021 02:07:56 GMT
"x-ows-header": Leading and trailing whitespace.
"x-obs-fold-header": Obsolete line folding.
"cache-control": max-age=60, must-revalidate
"example-dict": a=1,    b=2;x=1;y=2,   c=(a   b   c)
~~~

Since empty HTTP header fields are allowed, they are also able to be signed when present in a message. The canonicalized value is the empty string. This means that the following empty header:

~~~http-message
NOTE: '\' line wrapping per RFC 8792

X-Empty-Header: \

~~~

Is serialized by the [signature input generation algorithm](#create-sig-input) with an empty string value following the colon and space added after the content identifier.

~~~
NOTE: '\' line wrapping per RFC 8792

"x-empty-header": \

~~~

Note: these are shown here using the line wrapping algorithm in {{RFC8792}} due to limitations in the document format that strips trailing spaces from diagrams.

### Canonicalized Structured HTTP Fields {#http-header-structured}

If value of the the HTTP field in question is a structured field ({{!RFC8941}}), the component identifier MAY include the `sf` parameter to indicate it is a known structured field. If this
parameter is included with a component identifier, the HTTP field value MUST be serialized using the rules specified in {{Section 4 of RFC8941}} applicable to the type of the HTTP field. Note that this process
will replace any optional internal whitespace with a single space character, among other potential transformations of the value.

For example, the following dictionary field is a valid serialization:

~~~http-message
Example-Dict:  a=1,    b=2;x=1;y=2,   c=(a   b   c)
~~~

If included in the input string as-is, it would be:

~~~
"example-dict": a=1,    b=2;x=1;y=2,   c=(a   b   c)
~~~

However, if the `sf` parameter is added, the value is re-serialized as follows:

~~~
"example-dict";sf: a=1, b=2;x=1;y=2, c=(a b c)
~~~

The resulting string is used as the component value in {{http-header}}.

### Dictionary Structured Field Members {#http-header-dictionary}

An individual member in the value of a Dictionary Structured Field is identified by using the parameter `key` to indicate the member key as an `sf-string` value.

An individual member in the value of a Dictionary Structured Field is canonicalized by applying the serialization algorithm described in {{Section 4.1.2 of RFC8941}} on the member value and its parameters, without the dictionary key.

Each parameterized key for a given field MUST NOT appear more than once in the signature input. Parameterized keys MAY appear in any order.

If a dictionary key is named as a covered component but it does not occur in the dictionary, this MUST cause an error in the signature input string generation.

Following are non-normative examples of canonicalized values for Dictionary Structured Field Members given the following example header field, whose value is known to be a Dictionary:

~~~ http-message
Example-Dict:  a=1, b=2;x=1;y=2, c=(a   b    c)
~~~

The following example shows canonicalized values for different component identifiers of this field, presented using the signature input string format discussed in {{create-sig-input}}:

~~~
"example-dict";key="a": 1
"example-dict";key="b": 2;x=1;y=2
"example-dict";key="c": (a b c)
~~~

Note that the value for `key="c"` has been re-serialized.

## Derived Components {#derived-components}

In addition to HTTP fields, there are a number of different components that can be derived from the control data, processing context, or other aspects of the HTTP message being signed. Such derived components can be included in the signature input by defining a component identifier and the derivation method for its component value.

Derived component identifiers MUST start with the "at" `@` character. This differentiates derived component identifiers from HTTP field names, which cannot contain the `@` character as per {{Section 5.1 of SEMANTICS}}. Processors of HTTP Message Signatures MUST treat derived component identifiers separately from field names, as discussed in {{security-lazy-header-parser}}.

This specification defines the following derived component identifiers:

@signature-params
: The signature metadata parameters for this signature. ({{signature-params}})

@method
: The method used for a request. ({{content-request-method}})

@target-uri
: The full target URI for a request. ({{content-target-uri}})

@authority
: The authority of the target URI for a request. ({{content-request-authority}})

@scheme
: The scheme of the target URI for a request. ({{content-request-scheme}})

@request-target
: The request target. ({{content-request-target}})

@path
: The absolute path portion of the target URI for a request. ({{content-request-path}})

@query
: The query portion of the target URI for a request. ({{content-request-query}})

@query-params
: The parsed query parameters of the target URI for a request. ({{content-request-query-params}})

@status
: The status code for a response. ({{content-status-code}}).

@request-response
: A signature from a request message that resulted in this response message. ({{content-request-response}})

Additional derived component identifiers MAY be defined and registered in the HTTP Signatures Derived Component Identifier Registry. ({{content-registry}})

Derived components can be applied in one or more of three targets:

request:
: Values derived from and results applied to an HTTP request message as described in {{Section 3.4 of SEMANTICS.

response:
: Values derived from and results applied to an HTTP response message as described in {{Section 3.4 of SEMANTICS}}.

related-response:
: Values derived from an HTTP request message and results applied to the HTTP response message that is responding to that specific request.

A component identifier definition MUST define all targets to which it can be applied.

The component value MUST be derived from the HTTP message being signed or the context in which the derivation occurs. The derived component value MUST be of the following form:

~~~ abnf
derived-component-value = *VCHAR
~~~



### Signature Parameters {#signature-params}

HTTP Message Signatures have metadata properties that provide information regarding the signature's generation and verification, such as the set of covered components, a timestamp, identifiers for verification key material, and other utilities.

The signature parameters component identifier is `@signature-params`. This message component's value is REQUIRED as part of the [signature input string](#create-sig-input) but the component identifier MUST NOT be enumerated within the set of covered components itself.

The signature parameters component value is the serialization of the signature parameters for this signature, including the covered components set with all associated parameters. These parameters include any of the following:

* `created`: Creation time as an `sf-integer` UNIX timestamp value. Sub-second precision is not supported. Inclusion of this parameter is RECOMMENDED.
* `expires`: Expiration time as an `sf-integer` UNIX timestamp value. Sub-second precision is not supported.
* `nonce`: A random unique value generated for this signature as an `sf-string` value.
* `alg`: The HTTP message signature algorithm from the HTTP Message Signature Algorithm Registry, as an `sf-string` value.
* `keyid`: The identifier for the key material as an `sf-string` value.

Additional parameters can be defined in the [HTTP Signature Parameters Registry](#iana-param-contents).

The signature parameters component value is serialized as a parameterized inner list using the rules in {{Section 4 of RFC8941}} as follows:

1. Let the output be an empty string.
2. Determine an order for the component identifiers of the covered components, not including the `@signature-params` component identifier itself. Once this order is chosen, it cannot be changed. This order MUST be the same order as used in creating the signature input ({{create-sig-input}}).
3. Serialize the component identifiers of the covered components, including all parameters, as an ordered `inner-list` according to {{Section 4.1.1.1 of RFC8941}} and append this to the output.
4. Determine an order for any signature parameters. Once this order is chosen, it cannot be changed.
5. Append the parameters to the `inner-list` in the chosen order according to {{Section 4.1.1.2 of RFC8941}},
    skipping parameters that are not available or not used for this message signature.
6. The output contains the signature parameters component value.

Note that the `inner-list` serialization is used for the covered component value instead of the `sf-list` serialization
in order to facilitate this value's inclusion in message fields such as the `Signature-Input` field's dictionary,
as discussed in {{signature-input-header}}.

This example shows a canonicalized value for the parameters of a given signature:

~~~
NOTE: '\' line wrapping per RFC 8792

("@target-uri" "@authority" "date" "cache-control")\
  ;keyid="test-key-rsa-pss";alg="rsa-pss-sha512";\
  created=1618884475;expires=1618884775
~~~

Note that an HTTP message could contain [multiple signatures](#signature-multiple), but only the signature parameters used for a single signature are included in an entry.

### Method {#content-request-method}

The `@method` component identifier refers to the HTTP method of a request message. The component value of is canonicalized by taking the value of the method as a string. Note that the method name is case-sensitive as per {{SEMANTICS, Section 9.1}}, and conventionally standardized method names are uppercase US-ASCII.
If used, the `@method` component identifier MUST occur only once in the covered components.

For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@method` value:

~~~
"@method": POST
~~~

If used in a related-response, the `@method` component identifier refers to the associated component value of the request that triggered the response message being signed.

### Target URI {#content-target-uri}

The `@target-uri` component identifier refers to the target URI of a request message. The component value is the full absolute target URI of the request, potentially assembled from all available parts including the authority and request target as described in {{SEMANTICS, Section 7.1}}.
If used, the `@target-uri` component identifier MUST occur only once in the covered components.

For example, the following message sent over HTTPS:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@target-uri` value:

~~~
"@target-uri": https://www.example.com/path?param=value
~~~

If used in a related-response, the `@target-uri` component identifier refers to the associated component value of the request that triggered the response message being signed.

### Authority {#content-request-authority}

The `@authority` component identifier refers to the authority component of the target URI of the HTTP request message, as defined in {{SEMANTICS, Section 7.2}}. In HTTP 1.1, this is usually conveyed using the `Host` header, while in HTTP 2 and HTTP 3 it is conveyed using the `:authority` pseudo-header. The value is the fully-qualified authority component of the request, comprised of the host and, optionally, port of the request target, as a string.
The component value MUST be normalized according to the rules in {{SEMANTICS, Section 4.2.3}}. Namely, the host name is normalized to lowercase and the default port is omitted.
If used, the `@authority` component identifier MUST occur only once in the covered components.

For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@authority` component value:

~~~
"@authority": www.example.com
~~~

If used in a related-response, the `@authority` component identifier refers to the associated component value of the request that triggered the response message being signed.

The `@authority` derived component SHOULD be used instead signing the `Host` header directly, see {{security-not-fields}}.

### Scheme {#content-request-scheme}

The `@scheme` component identifier refers to the scheme of the target URL of the HTTP request message. The component value is the scheme as a string as defined in {{SEMANTICS, Section 4.2}}.
While the scheme itself is case-insensitive, it MUST be normalized to lowercase for
inclusion in the signature input string.
If used, the `@scheme` component identifier MUST occur only once in the covered components.

For example, the following request message requested over plain HTTP:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@scheme` value:

~~~
"@scheme": http
~~~

If used in a related-response, the `@scheme` component identifier refers to the associated component value of the request that triggered the response message being signed.

### Request Target {#content-request-target}

The `@request-target` component identifier refers to the full request target of the HTTP request message,
as defined in {{SEMANTICS, Section 7.1}}. The component value of the request target can take different forms,
depending on the type of request, as described below.
If used, the `@request-target` component identifier MUST occur only once in the covered components.

For HTTP 1.1, the component value is equivalent to the request target
portion of the request line. However, this value is more difficult to reliably construct in
other versions of HTTP. Therefore, it is NOT RECOMMENDED that this identifier be used
when versions of HTTP other than 1.1 might be in use.

The origin form value is combination of the absolute path and query components of the request URL. For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@request-target` component value:

~~~
"@request-target": /path?param=value
~~~

The following request to an HTTP proxy with the absolute-form value, containing the fully qualified target URI:

~~~ http-message
GET https://www.example.com/path?param=value HTTP/1.1
~~~

Would result in the following `@request-target` component value:

~~~
"@request-target": https://www.example.com/path?param=value
~~~

The following CONNECT request with an authority-form value, containing the host and port of the target:

~~~ http-message
CONNECT www.example.com:80 HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@request-target` component value:

~~~
"@request-target": www.example.com:80
~~~

The following OPTIONS request message with the asterisk-form value, containing a single asterisk `*` character:

~~~ http-message
OPTIONS * HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@request-target` component value:

~~~
"@request-target": *
~~~

If used in a related-response, the `@request-target` component identifier refers to the associated component value of the request that triggered the response message being signed.

### Path {#content-request-path}

The `@path` component identifier refers to the target path of the HTTP request message. The component value is the absolute path of the request target defined by {{RFC3986}}, with no query component and no trailing `?` character. The value is normalized according to the rules in {{SEMANTICS, Section 4.2.3}}. Namely, an empty path string is normalized as a single slash `/` character, and path components are represented by their values after decoding any percent-encoded octets.
If used, the `@path` component identifier MUST occur only once in the covered components.

For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@path` value:

~~~
"@path": /path
~~~

If used in a related-response, the `@path` identifier refers to the associated component value of the request that triggered the response message being signed.

### Query {#content-request-query}

The `@query` component identifier refers to the query component of the HTTP request message. The component value is the entire normalized query string defined by {{RFC3986}}, including the leading `?` character. The value is normalized according to the rules in {{SEMANTICS, Section 4.2.3}}. Namely, percent-encoded octets are decoded.
If used, the `@query` component identifier MUST occur only once in the covered components.

For example, the following request message:

~~~ http-message
POST /path?param=value&foo=bar&baz=batman HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@query` value:

~~~
"@query": ?param=value&foo=bar&baz=batman
~~~

The following request message:

~~~ http-message
POST /path?queryString HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@query` value:

~~~
"@query": ?queryString
~~~

If the query string is absent from the request message, the value is the leading `?` character alone:

~~~
"@query": ?
~~~

If used in a related-response, the `@query` component identifier refers to the associated component value of the request that triggered the response message being signed.

### Query Parameters {#content-request-query-params}

If a request target URI uses HTML form parameters in the query string as defined in [HTMLURL, Section 5](#HTMLURL),
the `@query-params` component identifier allows addressing of individual query parameters. The query parameters MUST be parsed according to [HTMLURL, Section 5.1](#HTMLURL), resulting in a list of (`nameString`, `valueString`) tuples.
The REQUIRED `name` parameter of each input identifier contains the `nameString` of a single query parameter as an `sf-string` value.
Several different named query parameters MAY be included in the covered components.
Single named parameters MAY occur in any order in the covered components.

The component value of a single named parameter is the the `valueString` of the named query parameter defined by [HTMLURL, Section 5.1](#HTMLURL), which is the value after percent-encoded octets are decoded.
Note that this value does not include any leading `?` characters, equals sign `=`, or separating `&` characters.
Named query parameters with an empty `valueString` are included with an empty string as the component value.

If a query parameter is named as a covered component but it does not occur in the query parameters, this MUST cause an error in the signature input string generation.

For example for the following request:

~~~ http-message
POST /path?param=value&foo=bar&baz=batman&qux= HTTP/1.1
Host: www.example.com
~~~

Indicating the `baz`, `qux` and `param` named query parameters in would result in the following `@query-param` value:

~~~
"@query-params";name="baz": batman
"@query-params";name="qux":
"@query-params";name="param": value
~~~

If a parameter name occurs multiple times in a request, all parameter values of that name MUST be included
in separate signature input lines in the order in which the parameters occur in the target URI. Note that in some implementations, the order of parsed query parameters is not stable, and this situation could lead to unexpected results. If multiple parameters are common within an application, it is RECOMMENDED to sign the entire query string using the `@query` component identifier defined in {{content-request-query}}.

If used in a related-response, the `@query-params` component identifier refers to the associated component value of the request that triggered the response message being signed.

### Status Code {#content-status-code}

The `@status` component identifier refers to the three-digit numeric HTTP status code of a response message as defined in {{SEMANTICS, Section 15}}. The component value is the serialized three-digit integer of the HTTP response code, with no descriptive text.
If used, the `@status` component identifier MUST occur only once in the covered components.

For example, the following response message:

~~~ http-message
HTTP/1.1 200 OK
Date: Fri, 26 Mar 2010 00:05:00 GMT
~~~

Would result in the following `@status` value:

~~~
"@status": 200
~~~

The `@status` component identifier MUST NOT be used in a request message.

### Request-Response Signature Binding {#content-request-response}

When a signed request message results in a signed response message, the `@request-response` component identifier can be used to cryptographically link the request and the response to each other by including the identified request signature value in the response's signature input without copying the value of the request's signature to the response directly. This component identifier has a single REQUIRED parameter:

`key`
: Identifies which signature from the response to sign.

The component value is the `sf-binary` representation of the signature value of the referenced request identified by the `key` parameter.

For example, when serving this signed request:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18
Signature-Input: sig1=("@method" "@authority" "@path" \
  "content-digest" "content-length" "content-type")\
  ;created=1618884475;keyid="test-key-rsa-pss"
Signature:  sig1=:LAH8BjcfcOcLojiuOBFWn0P5keD3xAOuJRGziCLuD8r5MW9S0\
  RoXXLzLSRfGY/3SF8kVIkHjE13SEFdTo4Af/fJ/Pu9wheqoLVdwXyY/UkBIS1M8Br\
  c8IODsn5DFIrG0IrburbLi0uCc+E2ZIIb6HbUJ+o+jP58JelMTe0QE3IpWINTEzpx\
  jqDf5/Df+InHCAkQCTuKsamjWXUpyOT1Wkxi7YPVNOjW4MfNuTZ9HdbD2Tr65+BXe\
  TG9ZS/9SWuXAc+BZ8WyPz0QRz//ec3uWXd7bYYODSjRAxHqX+S1ag3LZElYyUKaAI\
  jZ8MGOt4gXEwCSLDv/zqxZeWLj/PDkn6w==:

{"hello": "world"}
~~~

This would result in the following unsigned response message:

~~~ http-message
HTTP/1.1 503 Service Unavailable
Date: Tue, 20 Apr 2021 02:07:56 GMT
Content-Type: application/json
Content-Length: 62

{"busy": true, "message": "Your call is very important to us"}
~~~

To cryptographically link the response to the request, the server signs the response with its own key and includes the signature of `sig1` from the request in the covered components of the response. The signature input string for this example is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@status": 503
"content-length": 62
"content-type": application/json
"@request-response";key="sig1": :LAH8BjcfcOcLojiuOBFWn0P5keD3xAOuJR\
  GziCLuD8r5MW9S0RoXXLzLSRfGY/3SF8kVIkHjE13SEFdTo4Af/fJ/Pu9wheqoLVd\
  wXyY/UkBIS1M8Brc8IODsn5DFIrG0IrburbLi0uCc+E2ZIIb6HbUJ+o+jP58JelMT\
  e0QE3IpWINTEzpxjqDf5/Df+InHCAkQCTuKsamjWXUpyOT1Wkxi7YPVNOjW4MfNuT\
  Z9HdbD2Tr65+BXeTG9ZS/9SWuXAc+BZ8WyPz0QRz//ec3uWXd7bYYODSjRAxHqX+S\
  1ag3LZElYyUKaAIjZ8MGOt4gXEwCSLDv/zqxZeWLj/PDkn6w==:
"@signature-params": ("@status" "content-length" "content-type" \
  "@request-response";key="sig1");created=1618884479\
  ;keyid="test-key-ecc-p256"
~~~

The signed response message is:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

HTTP/1.1 503 Service Unavailable
Date: Tue, 20 Apr 2021 02:07:56 GMT
Content-Type: application/json
Content-Length: 62
Signature-Input: reqres=("@status" "content-length" "content-type" \
  "@request-response";key="sig1");created=1618884479\
  ;keyid="test-key-ecc-p256"
Signature: reqres=:JqzXLIjNd6VWVg/M7enbjWkOgsPmIK9vcoFQEkLD0SXNbFjR\
  6d+olsof1dv7xC7ygF1q0YKjVrbV2QlCpDxrHg==:

{"busy": true, "message": "Your call is very important to us"}
~~~

Since the request's signature value itself is not repeated in the response, the requester MUST keep the original signature value around long enough to validate the signature of the response that uses this component identifier.

Note that the ECDSA algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

The `@request-response` component identifier MUST NOT be used in a request message.

## Creating the Signature Input String {#create-sig-input}

The signature input is a US-ASCII string containing the canonicalized HTTP message components covered by the signature. The input to the signature input creation algorithm is the list of covered component identifiers and their associated values, along with any additional signature parameters. The output is the signature input string, which has the following form:

~~~ abnf
signature-input = *( signature-input-line LF ) signature-params-line
signature-input-line = component-identifier ":" SP
    ( derived-component-value / field-value )
signature-params-line = DQUOTE "@signature-params" DQUOTE ":" SP inner-list
~~~

To create the signature input string, the signer or verifier concatenates together entries for each identifier in the signature's covered components (including their parameters) using the following algorithm:

1. Let the output be an empty string.

2. For each message component item in the covered components set (in order):

    1. Append the component identifier for the covered component serialized according to the `component-identifier` rule. Note that this serialization places the component identifier in double quotes and appends any parameters outside of the quotes.

    2. Append a single colon `:`

    3. Append a single space " "

    4. Determine the component value for the component identifier.

        - If the component identifier starts with an "at" character (`@`), derive the component's value from the message according to the specific rules defined for the derived component identifier, as in {{derived-components}}. If the derived component identifier is unknown or the value cannot be derived, produce an error.

        - If the component identifier does not start with an "at" character (`@`), canonicalize the HTTP field value as described in {{http-header}}. If the value cannot be calculated, produce an error.

    5. Append the covered component's canonicalized component value.

    6. Append a single newline `\n`

3. Append the signature parameters component ({{signature-params}}) as follows:

    1. Append the component identifier for the signature parameters serialized according to the `component-identifier` rule, i.e. `"@signature-params"`

    2. Append a single colon `:`

    3. Append a single space " "

    4. Append the signature parameters' canonicalized component value as defined in {{signature-params}}

4. Return the output string.

If covered components reference a component identifier that cannot be resolved to a component value in the message, the implementation MUST produce an error and not create an input string. Such situations are included but not limited to:

 * The signer or verifier does not understand the derived component identifier.
 * The component identifier identifies a field that is not present in the message or whose value is malformed.
 * The component identifier indicates that a structured field serialization is used (via the `sf` parameter), but the field in question is known to not be a structured field or the type of structured field is not known to the implementation.
 * The component identifier is a dictionary member identifier that references a field that is not present in the message, is not a Dictionary Structured Field, or whose value is malformed.
 * The component identifier is a dictionary member identifier or a named query parameter identifier that references a member that is not present in the component value, or whose value is malformed. E.g., the identifier is `"example-dict";key="c"` and the value of the `Example-Dict` header field is `a=1, b=2`, which does not have the `c` value.

In the following non-normative example, the HTTP message being signed is the following request:

~~~ http-message
POST /foo?param=Value&Pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18

{"hello": "world"}
~~~

The covered components consist of the `@method`, `@path`, and `@authority` derived component identifiers followed by the `Content-Digest`, `Content-Length`, and `Content-Type` HTTP header fields, in order. The signature parameters consist of a creation timestamp of `1618884473` and a key identifier of `test-key-rsa-pss`. Note that no explicit `alg` parameter is given here since the verifier is assumed by the application to correctly use the RSA PSS algorithm based on the identified key. The signature input string for this message with these parameters is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@method": POST
"@authority": example.com
"@path": /foo
"content-digest": sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX\
  +TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
"content-length": 18
"content-type": application/json
"@signature-params": ("@method" "@authority" "@path" \
  "content-digest" "content-length" "content-type")\
  ;created=1618884473;keyid="test-key-rsa-pss"
~~~
{: title="Non-normative example Signature Input" artwork-name="example-sig-input" #example-sig-input}

Note that the example signature input here, or anywhere else within this specification, does not include the final newline that ends the displayed example.

# HTTP Message Signatures {#message-signatures}

An HTTP Message Signature is a signature over a string generated from a subset of the components of an HTTP message in addition to metadata about the signature itself. When successfully verified against an HTTP message, an HTTP Message Signature provides cryptographic proof that the message is semantically equivalent to the message for which the signature was generated, with respect to the subset of message components that was signed.

## Creating a Signature {#sign}

Creation of an HTTP message signature is a process that takes as its input the message and the requirements for the application. The output is a signature value and set of signature parameters that can be applied to the message.

In order to create a signature, a signer MUST follow the following algorithm:

1. The signer chooses an HTTP signature algorithm and key material for signing. The signer MUST choose key material that is appropriate
    for the signature's algorithm, and that conforms to any requirements defined by the algorithm, such as key size or format. The
    mechanism by which the signer chooses the algorithm and key material is out of scope for this document.

2. The signer sets the signature's creation time to the current time.

3. If applicable, the signer sets the signature's expiration time property to the time at which the signature is to expire. The expiration is a hint to the verifier, expressing the time at which the signer is no longer willing to vouch for the safety of the signature.

4. The signer creates an ordered set of component identifiers representing the message components to be covered by the signature, and attaches signature metadata parameters to this set. The serialized value of this is later used as the value of the `Signature-Input` field as described in {{signature-input-header}}.
   * Once an order of covered components is chosen, the order MUST NOT change for the life of the signature.
   * Each covered component identifier MUST be either an HTTP field in the message {{http-header}} or a derived component identifier listed in {{derived-components}} or its associated registry.
   * Signers of a request SHOULD include some or all of the message control data in the covered components, such as the `@method`, `@authority`, `@target-uri`, or some combination thereof.
   * Signers SHOULD include the `created` signature metadata parameter to indicate when the signature was created.
   * The `@signature-params` derived component identifier is not explicitly listed in the list of covered component identifiers, because it is required to always be present as the last line in the signature input. This ensures that a signature always covers its own metadata.
   * Further guidance on what to include in this set and in what order is out of scope for this document.

5. The signer creates the signature input string based on these signature parameters. ({{create-sig-input}})

6. The signer uses the `HTTP_SIGN` function to sign the signature input with the chosen signing algorithm using the key material chosen by the signer. The `HTTP_SIGN` primitive and several concrete signing algorithms are defined in in {{signature-methods}}.

7. The byte array output of the signature function is the HTTP message signature output value to be included in the `Signature` field as defined in {{signature-header}}.

For example, given the HTTP message and signature parameters in the example in {{create-sig-input}}, the example signature input string is signed with the `test-key-rsa-pss` key in {{example-key-rsa-pss-test}} and the RSA PSS algorithm described in {{method-rsa-pss-sha512}}, giving the following message signature output value, encoded in Base64:

~~~
NOTE: '\' line wrapping per RFC 8792

HIbjHC5rS0BYaa9v4QfD4193TORw7u9edguPh0AW3dMq9WImrlFrCGUDih47vAxi4L2\
YRZ3XMJc1uOKk/J0ZmZ+wcta4nKIgBkKq0rM9hs3CQyxXGxHLMCy8uqK488o+9jrptQ\
+xFPHK7a9sRL1IXNaagCNN3ZxJsYapFj+JXbmaI5rtAdSfSvzPuBCh+ARHBmWuNo1Uz\
VVdHXrl8ePL4cccqlazIJdC4QEjrF+Sn4IxBQzTZsL9y9TP5FsZYzHvDqbInkTNigBc\
E9cKOYNFCn4D/WM7F6TNuZO9EgtzepLWcjTymlHzK7aXq6Am6sfOrpIC49yXjj3ae6H\
RalVc/g==
~~~
{: title="Non-normative example signature value" #example-sig-value}

Note that the RSA PSS algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

## Verifying a Signature {#verify}

Verification of an HTTP message signature is a process that takes as its input the message (including `Signature` and `Signature-Input` fields) and the requirements for the application. The output of the verification is either a positive verification or an error.

In order to verify a signature, a verifier MUST follow the following algorithm:

1. Parse the `Signature` and `Signature-Input` fields as described in {{signature-input-header}} and {{signature-header}}, and extract the signatures to be verified.
    1. If there is more than one signature value present, determine which signature should be processed
        for this message based on the policy and configuration of the verifier. If an applicable signature is not found, produce an error.
    2. If the chosen `Signature` value does not have a corresponding `Signature-Input` value,
        produce an error.
2. Parse the values of the chosen `Signature-Input` field as a parameterized structured field inner list item (`inner-list`) to get the signature parameters for the
    signature to be verified.
3. Parse the value of the corresponding `Signature` field to get the byte array value of the signature
    to be verified.
4. Examine the signature parameters to confirm that the signature meets the requirements described
    in this document, as well as any additional requirements defined by the application such as which
    message components are required to be covered by the signature. ({{verify-requirements}})
5. Determine the verification key material for this signature. If the key material is known through external
    means such as static configuration or external protocol negotiation, the verifier will use that. If the key is
    identified in the signature parameters, the verifier will dereference this to appropriate key material to use
    with the signature. The verifier has to determine the trustworthiness of the key material for the context
    in which the signature is presented. If a key is identified that the verifier does not know, does
    not trust for this request, or does not match something preconfigured, the verification MUST fail.
6. Determine the algorithm to apply for verification:
    1. If the algorithm is known through external means such as static configuration or external protocol
        negotiation, the verifier will use this algorithm.
    2. If the algorithm is explicitly stated in the signature parameters using a value from the
        HTTP Message Signatures registry, the verifier will use the referenced algorithm.
    3. If the algorithm can be determined from the keying material, such as through an algorithm field
        on the key value itself, the verifier will use this algorithm.
    4. If the algorithm is specified in more that one location, such as through static configuration
        and the algorithm signature parameter, or the algorithm signature parameter and from
        the key material itself, the resolved algorithms MUST be the same. If the algorithms are
        not the same, the verifier MUST vail the verification.
7. Use the received HTTP message and the signature's metadata to recreate the signature input, using
    the process described in {{create-sig-input}}. The value of the `@signature-params` input is
    the value of the `Signature-Input` field for this signature serialized according to the rules described
    in {{signature-params}}, not including the signature's label from the `Signature-Input` field.
8. If the key material is appropriate for the algorithm, apply the appropriate `HTTP_VERIFY` cryptographic verification algorithm to the signature,
    recalculated signature input, key material, signature value. The `HTTP_VERIFY` primitive and several concrete algorithms are defined in
    {{signature-methods}}.
9. The results of the verification algorithm function are the final results of the cryptographic verification function.

If any of the above steps fail or produce an error, the signature validation fails.

For example, verifying the signature with the key `sig1` of the following message with the `test-key-rsa-pss` key in {{example-key-rsa-pss-test}} and the RSA PSS algorithm described in {{method-rsa-pss-sha512}}:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18
Signature-Input: sig1=("@method" "@authority" "@path" \
  "content-digest" "content-length" "content-type")\
  ;created=1618884473;keyid="test-key-rsa-pss"
Signature: sig1=:HIbjHC5rS0BYaa9v4QfD4193TORw7u9edguPh0AW3dMq9WImrl\
  FrCGUDih47vAxi4L2YRZ3XMJc1uOKk/J0ZmZ+wcta4nKIgBkKq0rM9hs3CQyxXGxH\
  LMCy8uqK488o+9jrptQ+xFPHK7a9sRL1IXNaagCNN3ZxJsYapFj+JXbmaI5rtAdSf\
  SvzPuBCh+ARHBmWuNo1UzVVdHXrl8ePL4cccqlazIJdC4QEjrF+Sn4IxBQzTZsL9y\
  9TP5FsZYzHvDqbInkTNigBcE9cKOYNFCn4D/WM7F6TNuZO9EgtzepLWcjTymlHzK7\
  aXq6Am6sfOrpIC49yXjj3ae6HRalVc/g==:

{"hello": "world"}
~~~

With the additional requirements that at least the method, path, authority, and cache-control be signed, and that the signature creation timestamp is recent enough at the time of verification, the verification passes.

### Enforcing Application Requirements {#verify-requirements}

The verification requirements specified in this document are intended as a baseline set of restrictions that are generally applicable to all use cases.  Applications using HTTP Message Signatures MAY impose requirements above and beyond those specified by this document, as appropriate for their use case.

Some non-normative examples of additional requirements an application might define are:

- Requiring a specific set of header fields to be signed (e.g., `Authorization`, `Digest`).
- Enforcing a maximum signature age from the time of the `created` time stamp.
- Rejection of signatures past the expiration time in the `expires` time stamp. Note that the expiration time is a hint from the signer and that a verifier can always reject a signature ahead of its expiration time.
- Prohibition of certain signature metadata parameters, such as runtime algorithm signaling with the `alg` parameter when the algorithm is determined from the key information.
- Ensuring successful dereferencing of the `keyid` parameter to valid and appropriate key material.
- Prohibiting the use of certain algorithms, or mandating the use of a specific algorithm.
- Requiring keys to be of a certain size (e.g., 2048 bits vs. 1024 bits).
- Enforcing uniqueness of a `nonce` value.

Application-specific requirements are expected and encouraged.  When an application defines additional requirements, it MUST enforce them during the signature verification process, and signature verification MUST fail if the signature does not conform to the application's requirements.

Applications MUST enforce the requirements defined in this document.  Regardless of use case, applications MUST NOT accept signatures that do not conform to these requirements.

## Signature Algorithm Methods {#signature-methods}

HTTP Message signatures MAY use any cryptographic digital signature or MAC method that is appropriate for the key material,
environment, and needs of the signer and verifier.

Each signature algorithm method takes as its input the signature input string defined in {{create-sig-input}} as a byte array (`M`), the signing key material
(`Ks`), and outputs the signature output as a byte array (`S`):

~~~
HTTP_SIGN (M, Ks)  ->  S
~~~

Each verification algorithm method takes as its input the recalculated signature input string defined in {{create-sig-input}} as a byte array (`M`), the verification key
material (`Kv`), and the presented signature to be verified as a byte array (`S`) and outputs the verification result (`V`) as a boolean:

~~~
HTTP_VERIFY (M, Kv, S) -> V
~~~

This section contains several common algorithm methods. The method to use can be communicated through the explicit algorithm signature parameter `alg`
defined in {{signature-params}}, by reference to the key material, or through mutual agreement between the signer and verifier.

### RSASSA-PSS using SHA-512 {#method-rsa-pss-sha512}

To sign using this algorithm, the signer applies the `RSASSA-PSS-SIGN (K, M)` function {{RFC8017}} with the signer's private signing key (`K`) and
the signature input string (`M`) ({{create-sig-input}}).
The mask generation function is `MGF1` as specified in {{RFC8017}} with a hash function of SHA-512 {{RFC6234}}.
The salt length (`sLen`) is 64 bytes.
The hash function (`Hash`) SHA-512 {{RFC6234}} is applied to the signature input string to create
the digest content to which the digital signature is applied.
The resulting signed content byte array (`S`) is the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `RSASSA-PSS-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key portion of the verification key material (`(n, e)`) and the signature input string (`M`) re-created as described in {{verify}}.
The mask generation function is `MGF1` as specified in {{RFC8017}} with a hash function of SHA-512 {{RFC6234}}.
The salt length (`sLen`) is 64 bytes.
The hash function (`Hash`) SHA-512 {{RFC6234}} is applied to the signature input string to create the digest content to which the verification function is applied.
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The results of the verification function indicate if the signature presented is valid.

Note that the output of RSA PSS algorithms are non-deterministic, and therefore it is not correct to re-calculate a new signature on the signature input and compare the results to an existing signature. Instead, the verification algorithm defined here needs to be used. See {{security-nondeterministic}}.

Use of this algorithm can be indicated at runtime using the `rsa-pss-sha512` value for the `alg` signature parameter.

### RSASSA-PKCS1-v1_5 using SHA-256 {#method-rsa-v1_5-sha256}

To sign using this algorithm, the signer applies the `RSASSA-PKCS1-V1_5-SIGN (K, M)` function {{RFC8017}} with the signer's private signing key (`K`) and
the signature input string (`M`) ({{create-sig-input}}).
The hash SHA-256 {{RFC6234}} is applied to the signature input string to create
the digest content to which the digital signature is applied.
The resulting signed content byte array (`S`) is the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `RSASSA-PKCS1-V1_5-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key portion of the verification key material (`(n, e)`) and the signature input string (`M`) re-created as described in {{verify}}.
The hash function SHA-256 {{RFC6234}} is applied to the signature input string to create the digest content to which the verification function is applied.
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The results of the verification function are compared to the http message signature to determine if the signature presented is valid.

Use of this algorithm can be indicated at runtime using the `rsa-v1_5-sha256` value for the `alg` signature parameter.

### HMAC using SHA-256 {#method-hmac-sha256}

To sign and verify using this algorithm, the signer applies the `HMAC` function {{RFC2104}} with the shared signing key (`K`) and
the signature input string (`text`) ({{create-sig-input}}).
The hash function SHA-256 {{RFC6234}} is applied to the signature input string to create the digest content to which the HMAC is applied, giving the signature result.

For signing, the resulting value is the HTTP message signature output used in {{sign}}.

For verification, the verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The output of the HMAC function is compared to the value of the HTTP message signature, and the results of the comparison determine the validity of the signature presented.

Use of this algorithm can be indicated at runtime using the `hmac-sha256` value for the `alg` signature parameter.

### ECDSA using curve P-256 DSS and SHA-256 {#method-ecdsa-p256-sha256}

To sign using this algorithm, the signer applies the `ECDSA` algorithm {{FIPS186-4}} using curve P-256 with the signer's private signing key and
the signature input string ({{create-sig-input}}).
The hash SHA-256 {{RFC6234}} is applied to the signature input string to create
the digest content to which the digital signature is applied, (`M`).
The signature algorithm returns two integer values, `r` and `s`. These are both encoded in big-endian unsigned integers, zero-padded to 32-octets each. These encoded values are concatenated into a single 64-octet array consisting of the encoded value of `r` followed by the encoded value of `s`. The resulting concatenation of `(r, s)` is byte array of the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `ECDSA` algorithm {{FIPS186-4}}  using the public key portion of the verification key material and the signature input string re-created as described in {{verify}}.
The hash function SHA-256 {{RFC6234}} is applied to the signature input string to create the digest content to which the signature verification function is applied, (`M`).
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}. This value is a 64-octet array consisting of the encoded values of `r` and `s` concatenated in order. These are both encoded in big-endian unsigned integers, zero-padded to 32-octets each. The resulting signature value `(r, s)` is used as input to the signature verification function.
The results of the verification function indicate if the signature presented is valid.

Note that the output of ECDSA algorithms are non-deterministic, and therefore it is not correct to re-calculate a new signature on the signature input and compare the results to an existing signature. Instead, the verification algorithm defined here needs to be used. See {{security-nondeterministic}}.

Use of this algorithm can be indicated at runtime using the `ecdsa-p256-sha256` value for the `alg` signature parameter.

### EdDSA using curve edwards25519 {#method-ed25519}

To sign using this algorithm, the signer applies the `Ed25519` algorithm {{Section 5.1.6 of RFC8032}} with the signer's private signing key and
the signature input string ({{create-sig-input}}).
The signature input string is taken as the input message (`M`) with no pre-hash function.
The signature is a 64-octet concatenation of `R` and `S` as specified in {{Section 5.1.6 of RFC8032}}, and this is taken as a byte array for the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the signer applies the `Ed25519` algorithm {{Section 5.1.7 of RFC8032}} using the public key portion of the verification key material (`A`) and the signature input string re-created as described in {{verify}}.
The signature input string is taken as the input message (`M`) with no pre-hash function.
The signature to be verified is processed as the 64-octet concatenation of `R` and `S` as specified in {{Section 5.1.7 of RFC8032}}.
The results of the verification function indicate if the signature presented is valid.

Use of this algorithm can be indicated at runtime using the `ed25519` value for the `alg` signature parameter.

### JSON Web Signature (JWS) algorithms {#method-jose}

If the signing algorithm is a JOSE signing algorithm from the JSON Web Signature and Encryption Algorithms Registry established by {{RFC7518}}, the
JWS algorithm definition determines the signature and hashing algorithms to apply for both signing and verification.

For both signing and verification, the HTTP messages signature input string ({{create-sig-input}}) is used as the entire "JWS Signing Input".
The JOSE Header defined in {{RFC7517}} is not used, and the signature input string is not first encoded in Base64 before applying the algorithm.
The output of the JWS signature is taken as a byte array prior to the Base64url encoding used in JOSE.

The JWS algorithm MUST NOT be `none` and MUST NOT be any algorithm with a JOSE Implementation Requirement of `Prohibited`.

JWA algorithm values from the JSON Web Signature and Encryption Algorithms Registry are not included as signature parameters. In fact, the explicit `alg` signature parameter is not used at all when using JOSE signing algorithms, as the JWS algorithm can be signaled using JSON Web Keys or other mechanisms common to JOSE implementations.

# Including a Message Signature in a Message

Message signatures can be included within an HTTP message via the `Signature-Input` and `Signature` HTTP fields, both defined within this specification. When attached to a message, an HTTP message signature is identified by a label. This label MUST be unique within a given HTTP message and MUST be used in both the `Signature-Input` and `Signature`. The label is chosen by the signer, except where a specific label is dictated by protocol negotiations.

An HTTP message signature MUST use both fields containing the same labels:
the `Signature` HTTP field contains the signature value, while the `Signature-Input` HTTP field identifies the covered components and parameters that describe how the signature was generated. Each field contains labeled values and MAY contain multiple labeled values, where the labels determine the correlation between the `Signature` and `Signature-Input` fields.

## The 'Signature-Input' HTTP Field {#signature-input-header}

The `Signature-Input` HTTP field is a Dictionary Structured Field {{!RFC8941}} containing the metadata for one or more message signatures generated from components within the HTTP message. Each member describes a single message signature. The member's name is an identifier that uniquely identifies the message signature within the context of the HTTP message. The member's value is the serialization of the covered components including all signature metadata parameters, using the serialization process defined in {{signature-params}}.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig1=("@method" "@target-uri" "@authority" \
  "content-digest" "cache-control");\
  created=1618884475;keyid="test-key-rsa-pss"
~~~

To facilitate signature validation, the `Signature-Input` field value MUST contain the same serialized value used
in generating the signature input string's `@signature-params` value.

The signer MAY include the `Signature-Input` field as a trailer to facilitate signing a message after its content has been processed by the signer. However, since intermediaries are allowed to drop trailers as per {{SEMANTICS}}, it is RECOMMENDED that the `Signature-Input` HTTP field be included only as a header to avoid signatures being inadvertently stripped from a message.

Multiple `Signature-Input` fields MAY be included in a single HTTP message. The signature labels MUST be unique across all field values.

## The 'Signature' HTTP Field {#signature-header}

The `Signature` HTTP field is a Dictionary Structured field {{!RFC8941}} containing one or more message signatures generated from components within the HTTP message. Each member's name is a signature identifier that is present as a member name in the `Signature-Input` Structured field within the HTTP message. Each member's value is a Byte Sequence containing the signature value for the message signature identified by the member name. Any member in the `Signature` HTTP field that does not have a corresponding member in the HTTP message's `Signature-Input` HTTP field MUST be ignored.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature: sig1=:P0wLUszWQjoi54udOtydf9IWTfNhy+r53jGFj9XZuP4uKwxyJo\
  1RSHi+oEF1FuX6O29d+lbxwwBao1BAgadijW+7O/PyezlTnqAOVPWx9GlyntiCiHz\
  C87qmSQjvu1CFyFuWSjdGa3qLYYlNm7pVaJFalQiKWnUaqfT4LyttaXyoyZW84jS8\
  gyarxAiWI97mPXU+OVM64+HVBHmnEsS+lTeIsEQo36T3NFf2CujWARPQg53r58Rmp\
  Z+J9eKR2CD6IJQvacn5A4Ix5BUAVGqlyp8JYm+S/CWJi31PNUjRRCusCVRj05NrxA\
  BNFv3r5S9IXf2fYJK+eyW4AiGVMvMcOg==:
~~~

The signer MAY include the `Signature` field as a trailer to facilitate signing a message after its content has been processed by the signer. However, since intermediaries are allowed to drop trailers as per {{SEMANTICS}}, it is RECOMMENDED that the `Signature-Input` HTTP field be included only as a header to avoid signatures being inadvertently stripped from a message.

Multiple `Signature` fields MAY be included in a single HTTP message. The signature labels MUST be unique across all field values.

## Multiple Signatures {#signature-multiple}

Multiple distinct signatures MAY be included in a single message. Each distinct signature MUST have a unique label. Since `Signature-Input` and `Signature` are both defined as Dictionary Structured fields, they can be used to include multiple signatures within the same HTTP message by using distinct signature labels. These multiple signatures could be added all by the same signer or could come from several different signers. For example, a signer may include multiple signatures signing the same message components with different keys or algorithms to support verifiers with different capabilities, or a reverse proxy may include information about the client in fields when forwarding the request to a service host, including a signature over the client's original signature values.

The following is a non-normative example starts with a signed request from the client. The proxy takes this request validates the client's signature.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18
Signature-Input: sig1=("@method" "@authority" "@path" \
  "content-digest" "content-length" "content-type")\
  ;created=1618884475;keyid="test-key-rsa-pss"
Signature:  sig1=:LAH8BjcfcOcLojiuOBFWn0P5keD3xAOuJRGziCLuD8r5MW9S0\
  RoXXLzLSRfGY/3SF8kVIkHjE13SEFdTo4Af/fJ/Pu9wheqoLVdwXyY/UkBIS1M8Br\
  c8IODsn5DFIrG0IrburbLi0uCc+E2ZIIb6HbUJ+o+jP58JelMTe0QE3IpWINTEzpx\
  jqDf5/Df+InHCAkQCTuKsamjWXUpyOT1Wkxi7YPVNOjW4MfNuTZ9HdbD2Tr65+BXe\
  TG9ZS/9SWuXAc+BZ8WyPz0QRz//ec3uWXd7bYYODSjRAxHqX+S1ag3LZElYyUKaAI\
  jZ8MGOt4gXEwCSLDv/zqxZeWLj/PDkn6w==:

{"hello": "world"}
~~~

The proxy then alters the message before forwarding it on to the origin server, changing the target host and adding the `Forwarded` header defined in {{RFC7239}}.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: origin.host.internal.example
Date: Tue, 20 Apr 2021 02:07:56 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18
Forwarded: for=192.0.2.123
Signature-Input: sig1=("@method" "@authority" "@path" \
  "content-digest" "content-length" "content-type")\
  ;created=1618884475;keyid="test-key-rsa-pss"
Signature:  sig1=:LAH8BjcfcOcLojiuOBFWn0P5keD3xAOuJRGziCLuD8r5MW9S0\
  RoXXLzLSRfGY/3SF8kVIkHjE13SEFdTo4Af/fJ/Pu9wheqoLVdwXyY/UkBIS1M8Br\
  c8IODsn5DFIrG0IrburbLi0uCc+E2ZIIb6HbUJ+o+jP58JelMTe0QE3IpWINTEzpx\
  jqDf5/Df+InHCAkQCTuKsamjWXUpyOT1Wkxi7YPVNOjW4MfNuTZ9HdbD2Tr65+BXe\
  TG9ZS/9SWuXAc+BZ8WyPz0QRz//ec3uWXd7bYYODSjRAxHqX+S1ag3LZElYyUKaAI\
  jZ8MGOt4gXEwCSLDv/zqxZeWLj/PDkn6w==:

{"hello": "world"}
~~~

The proxy includes the client's signature value under the label `sig1`, which the proxy signs in addition to the `Forwarded` header. Note that since the client's signature already covers the client's `Signature-Input` value for `sig1`, this value is transitively covered by the proxy's signature and need not be added explicitly. The proxy identifies its own key and algorithm and, in this example, includes an expiration for the signature to indicate to downstream systems that the proxy will not vouch for this signed message past this short time window. This results in a signature input string of:

~~~
NOTE: '\' line wrapping per RFC 8792

"signature";key="sig1": :LAH8BjcfcOcLojiuOBFWn0P5keD3xAOuJRGziCLuD8\
  r5MW9S0RoXXLzLSRfGY/3SF8kVIkHjE13SEFdTo4Af/fJ/Pu9wheqoLVdwXyY/UkB\
  IS1M8Brc8IODsn5DFIrG0IrburbLi0uCc+E2ZIIb6HbUJ+o+jP58JelMTe0QE3IpW\
  INTEzpxjqDf5/Df+InHCAkQCTuKsamjWXUpyOT1Wkxi7YPVNOjW4MfNuTZ9HdbD2T\
  r65+BXeTG9ZS/9SWuXAc+BZ8WyPz0QRz//ec3uWXd7bYYODSjRAxHqX+S1ag3LZEl\
  YyUKaAIjZ8MGOt4gXEwCSLDv/zqxZeWLj/PDkn6w==:
"forwarded": for=192.0.2.123
"@signature-params": ("signature";key="sig1" "forwarded")\
  ;created=1618884480;expires=1618884540;keyid="test-key-rsa"\
  ;alg="rsa-v1_5-sha256"
~~~

And a signature output value of:

~~~
NOTE: '\' line wrapping per RFC 8792

G1WLTL4/9PGSKEQbSAMypZNk+I2dpLJ6qvl2JISahlP31OO/QEUd8/HdO2O7vYLi5k3\
JIiAK3UPK4U+kvJZyIUidsiXlzRI+Y2se3SGo0D8dLfhG95bKr6ukYXl60QHpsGRTfS\
iwdtvYKXGpKNrMlISJYd+oGrGRyI9gbCy0aFhc6I/okIMLeK4g9PgzpC3YTwhUQ98KI\
BNLWHgREfBgJxjPbxFlsgJ9ykPviLj8GKJ81HwsK3XM9P7WaS7fMGOt8h1kSqgkZQB9\
YqiIo+WhHvJa7iPy8QrYFKzx9BBEY6AwfStZAsXXz3LobZseyxsYcLJLs8rY0wVA9NP\
sxKrHGA==
~~~

These values are added to the HTTP request message by the proxy. The original signature is included under the identifier `sig1`, and the reverse proxy's signature is included under the label `proxy_sig`. The proxy uses the key `test-key-rsa` to create its signature using the `rsa-v1_5-sha256` signature algorithm, while the client's original signature was made using the key id of `test-key-rsa-pss` and an RSA PSS signature algorithm.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: origin.host.internal.example
Date: Tue, 20 Apr 2021 02:07:56 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18
Forwarded: for=192.0.2.123
Signature-Input: sig1=("@method" "@authority" "@path" \
    "content-digest" "content-length" "content-type")\
    ;created=1618884475;keyid="test-key-rsa-pss", \
  proxy_sig=("signature";key="sig1" "forwarded")\
    ;created=1618884480;expires=1618884540;keyid="test-key-rsa"\
    ;alg="rsa-v1_5-sha256"
Signature:  sig1=:LAH8BjcfcOcLojiuOBFWn0P5keD3xAOuJRGziCLuD8r5MW9S0\
    RoXXLzLSRfGY/3SF8kVIkHjE13SEFdTo4Af/fJ/Pu9wheqoLVdwXyY/UkBIS1M8\
    Brc8IODsn5DFIrG0IrburbLi0uCc+E2ZIIb6HbUJ+o+jP58JelMTe0QE3IpWINT\
    EzpxjqDf5/Df+InHCAkQCTuKsamjWXUpyOT1Wkxi7YPVNOjW4MfNuTZ9HdbD2Tr\
    65+BXeTG9ZS/9SWuXAc+BZ8WyPz0QRz//ec3uWXd7bYYODSjRAxHqX+S1ag3LZE\
    lYyUKaAIjZ8MGOt4gXEwCSLDv/zqxZeWLj/PDkn6w==:, \
  proxy_sig=:G1WLTL4/9PGSKEQbSAMypZNk+I2dpLJ6qvl2JISahlP31OO/QEUd8/\
    HdO2O7vYLi5k3JIiAK3UPK4U+kvJZyIUidsiXlzRI+Y2se3SGo0D8dLfhG95bKr\
    6ukYXl60QHpsGRTfSiwdtvYKXGpKNrMlISJYd+oGrGRyI9gbCy0aFhc6I/okIML\
    eK4g9PgzpC3YTwhUQ98KIBNLWHgREfBgJxjPbxFlsgJ9ykPviLj8GKJ81HwsK3X\
    M9P7WaS7fMGOt8h1kSqgkZQB9YqiIo+WhHvJa7iPy8QrYFKzx9BBEY6AwfStZAs\
    XXz3LobZseyxsYcLJLs8rY0wVA9NPsxKrHGA==:

{"hello": "world"}
~~~

The proxy's signature and the client's original signature can be verified independently for the same message, based on the needs of the application. Since the proxy's signature covers the client signature, the backend service fronted by the proxy can trust that the proxy has validated the incoming signature.

# Requesting Signatures

While a signer is free to attach a signature to a request or response without prompting, it is often desirable for a potential verifier to signal that it expects a signature from a potential signer using the `Accept-Signature` field.

The message to which the requested signature is applied is known as the "target message". When the `Accept-Signature` field is sent in an HTTP Request message, the field indicates that the client desires the server to sign the response using the identified parameters and the target message is the response to this request. All responses from resources that support such signature negotiation SHOULD either be uncacheable or contain a `Vary` header field that lists `Accept-Signature`, in order to prevent a cache from returning a response with a signature intended for a different request.

When the `Accept-Signature` field is used in an HTTP Response message, the field indicates that the server desires the client to sign its next request to the server with the identified parameters, and the target message is the client's next request. The client can choose to also continue signing future requests to the same server in the same way.

The target message of an `Accept-Signature` field MUST include all labeled signatures indicated in the `Accept-Header` signature, each covering the same identified components of the `Accept-Signature` field.

The sender of an `Accept-Signature` field MUST include identifiers that are appropriate for the type of the target message. For example, if the target message is a response, the identifiers can not include the `@status` identifier.


## The Accept-Signature Field {#accept-signature-header}

The `Accept-Signature` HTTP header field is a Dictionary Structured field {{!RFC8941}} containing the metadata for one or more requested message signatures to be generated from message components of the target HTTP message. Each member describes a single message signature. The member's name is an identifier that uniquely identifies the requested message signature within the context of the target HTTP message. The member's value is the serialization of the desired covered components of the target message, including any allowed signature metadata parameters, using the serialization process defined in {{signature-params}}.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Accept-Signature: sig1=("@method" "@target-uri" "@authority" \
  "content-digest" "cache-control");\
  created=1618884475;keyid="test-key-rsa-pss"
~~~

The requested signature MAY include parameters, such as a desired algorithm or key identifier. These parameters MUST NOT include parameters that the signer is expected to generate, including the `created` and `nonce` parameters.

## Processing an Accept-Signature

The receiver of an `Accept-Signature` field fulfills that header as follows:

1. Parse the field value as a Dictionary
2. For each member of the dictionary:
    1. The name of the member is the label of the output signature as specified in {{signature-input-header}}
    2. Parse the value of the member to obtain the set of covered component identifiers
    3. Process the requested parameters, such as the signing algorithm and key material. If any requested parameters cannot be fulfilled, or if the requested parameters conflict with those deemed appropriate to the target message, the process fails and returns an error.
    4. Select any additional parameters necessary for completing the signature
    5. Create the `Signature-Input` and `Signature` header values and associate them with the label
3. Optionally create any additional `Signature-Input` and `Signature` values, with unique labels not found in the `Accept-Signature` field
4. Combine all labeled `Signature-Input` and `Signature` values and attach both headers to the target message

Note that by this process, a signature applied to a target message MUST have the same label, MUST have the same set of covered component, and MAY have additional parameters. Also note that the target message MAY include additional signatures not specified by the `Accept-Signature` field.

# IANA Considerations {#iana}

IANA is requested to create three registries and to populate those registries with initial values as described in this section.

## HTTP Signature Algorithms Registry {#hsa-registry}

This document defines HTTP Signature Algorithms, for which IANA is asked to create and maintain a new registry titled "HTTP Signature Algorithms".  Initial values for this registry are given in {{iana-hsa-contents}}.  Future assignments and modifications to existing assignment are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-hsa-template}}.

Algorithms referenced by algorithm identifiers have to be fully defined with all parameters fixed. Algorithm identifiers in this registry are to be interpreted as whole string values and not as a combination of parts. That is to say, it is expected that implementors understand `rsa-pss-sha512` as referring to one specific algorithm with its hash, mask, and salt values set as defined here. Implementors do not parse out the `rsa`, `pss`, and `sha512` portions of the identifier to determine parameters of the signing algorithm from the string.

Algorithms added to this registry MUST NOT be aliases for other entries in the registry.

### Registration Template {#iana-hsa-template}

{: vspace="0"}
Algorithm Name:
: An identifier for the HTTP Signature Algorithm. The name MUST be an ASCII string consisting only of lower-case characters (`"a"` - `"z"`), digits (`"0"` - `"9"`), and hyphens (`"-"`), and SHOULD NOT exceed 20 characters in length.  The identifier MUST be unique within the context of the registry.

Status:
: A brief text description of the status of the algorithm.  The description MUST begin with one of "Active" or "Deprecated", and MAY provide further context or explanation as to the reason for the status.

Description:
: A brief description of the algorithm used to sign the signature input string.

Specification document(s):
: Reference to the document(s) that specify the token endpoint
    authorization method, preferably including a URI that can be used
    to retrieve a copy of the document(s).  An indication of the
    relevant sections may also be included but is not required.

### Initial Contents {#iana-hsa-contents}

|Algorithm Name|Status|Description|Specification document(s)|
|`rsa-pss-sha512`|Active|RSASSA-PSS using SHA-512|\[\[This document\]\], {{method-rsa-pss-sha512}}|
|`rsa-v1_5-sha256`|Active|RSASSA-PKCS1-v1_5 using SHA-256|\[\[This document\]\], {{method-rsa-v1_5-sha256}}|
|`hmac-sha256`|Active|HMAC using SHA-256|\[\[This document\]\], {{method-hmac-sha256}}|
|`ecdsa-p256-sha256`|Active|ECDSA using curve P-256 DSS and SHA-256|\[\[This document\]\], {{method-ecdsa-p256-sha256}}|
|`ed25519`|Active|Edwards Curve DSA using curve edwards25519|\[\[This document\]\], {{method-ed25519}}|

## HTTP Signature Metadata Parameters Registry {#param-registry}

This document defines the signature parameters structure, the values of which may have parameters containing metadata about a message signature. IANA is asked to create and maintain a new registry titled "HTTP Signature Metadata Parameters" to record and maintain the set of parameters defined for use with member values in the signature parameters structure. Initial values for this registry are given in {{iana-param-contents}}.  Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-param-template}}.

### Registration Template {#iana-param-template}

{: vspace="0"}
Name:
: An identifier for the HTTP signature metadata parameter. The name MUST be an ASCII string consisting only of lower-case characters (`"a"` - `"z"`), digits (`"0"` - `"9"`), and hyphens (`"-"`), and SHOULD NOT exceed 20 characters in length.  The identifier MUST be unique within the context of the registry.

Description:
: A brief description of the metadata parameter and what it represents.

Specification document(s):
: Reference to the document(s) that specify the token endpoint
    authorization method, preferably including a URI that can be used
    to retrieve a copy of the document(s).  An indication of the
    relevant sections may also be included but is not required.


### Initial Contents {#iana-param-contents}

The table below contains the initial contents of the HTTP Signature Metadata Parameters Registry.  Each row in the table represents a distinct entry in the registry.

|Name|Description|Specification document(s)|
|--- |--- |--- |
|`alg`|Explicitly declared signature algorithm|{{signature-params}} of this document|
|`created`|Timestamp of signature creation| {{signature-params}} of this document|
|`expires`|Timestamp of proposed signature expiration| {{signature-params}} of this document|
|`keyid`|Key identifier for the signing and verification keys used to create this signature| {{signature-params}} of this document|
|`nonce`|A single-use nonce value| {{signature-params}} of this document|
{: title="Initial contents of the HTTP Signature Metadata Parameters Registry." }

## HTTP Signature Derived Component Identifiers Registry {#content-registry}

This document defines a method for canonicalizing HTTP message components, including components that can be derived from the context of the HTTP message outside of the HTTP fields. These components are identified by a unique string, known as the component identifier. Component identifiers for derived components always start with the "@" (at) symbol to distinguish them from HTTP header fields. IANA is asked to create and maintain a new registry typed "HTTP Signature Derived Component Identifiers" to record and maintain the set of non-field component identifiers and the methods to produce their associated component values. Initial values for this registry are given in {{iana-content-contents}}.  Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-content-template}}.

### Registration Template {#iana-content-template}

{: vspace="0"}
Identifier:
: An identifier for the HTTP derived component identifier. The name MUST begin with the `"@"` character followed by an ASCII string consisting only of lower-case characters (`"a"` - `"z"`), digits (`"0"` - `"9"`), and hyphens (`"-"`), and SHOULD NOT exceed 20 characters in length.  The identifier MUST be unique within the context of the registry.

Status:
: A brief text description of the status of the algorithm.  The description MUST begin with one of "Active" or "Deprecated", and MAY provide further context or explanation as to the reason for the status.

Target:
: The valid message targets for the derived parameter. MUST be one of the values "Request", "Request, Response", "Request, Related-Response", or "Related-Response". The semantics of these are defined in {{derived-components}}.

Specification document(s):
: Reference to the document(s) that specify the token endpoint
    authorization method, preferably including a URI that can be used
    to retrieve a copy of the document(s).  An indication of the
    relevant sections may also be included but is not required.

### Initial Contents {#iana-content-contents}

The table below contains the initial contents of the HTTP Signature Derived Component Identifiers Registry.

|Identifier|Status|Target|Specification document(s)|
|--- |--- |--- |--- |
|`@signature-params`| Active | Request, Response | {{signature-params}} of this document|
|`@method`| Active | Request, Related-Response | {{content-request-method}} of this document|
|`@authority`| Active | Request, Related-Response | {{content-request-authority}} of this document|
|`@scheme`| Active | Request, Related-Response | {{content-request-scheme}} of this document|
|`@target-uri`| Active | Request, Related-Response | {{content-target-uri}} of this document|
|`@request-target`| Active | Request, Related-Response | {{content-request-target}} of this document|
|`@path`| Active | Request, Related-Response | {{content-request-path}} of this document|
|`@query`| Active | Request, Related-Response | {{content-request-query}} of this document|
|`@query-params`| Active | Request, Related-Response | {{content-request-query-params}} of this document|
|`@status`| Active | Response | {{content-status-code}} of this document|
|`@request-response`|Active | Related-Response | {{content-request-response}} of this document|
{: title="Initial contents of the HTTP Signature Derived Component Identifiers Registry." }

# Security Considerations {#security}

In order for an HTTP message to be considered covered by a signature, all of the following conditions have to be true:

- a signature is expected or allowed on the message by the verifier
- the signature exists on the message
- the signature is verified against the identified key material and algorithm
- the key material and algorithm are appropriate for the context of the message
- the signature is within expected time boundaries
- the signature covers the expected content, including any critical components

## Signature Verification Skipping {#security-ignore}

HTTP Message Signatures only provide security if the signature is verified by the verifier. Since the message to which the signature is attached remains a valid HTTP message without the signature fields, it is possible for a verifier to ignore the output of the verification function and still process the message. Common reasons for this could be relaxed requirements in a development environment or a temporary suspension of enforcing verification during debugging an overall system. Such temporary suspensions are difficult to detect under positive-example testing since a good signature will always trigger a valid response whether or not it has been checked.

To detect this, verifiers should be tested using both valid and invalid signatures, ensuring that the invalid signature fails as expected.

## Use of TLS {#security-tls}

The use of HTTP Message Signatures does not negate the need for TLS or its equivalent to protect information in transit. Message signatures provide message integrity over the covered message components but do not provide any confidentiality for the communication between parties.

TLS provides such confidentiality between the TLS endpoints. As part of this, TLS also protects the signature data itself from being captured by an attacker, which is an important step in preventing [signature replay](#security-replay).

When TLS is used, it needs to be deployed according to the recommendations in {{BCP195}}.

## Signature Replay {#security-replay}

Since HTTP Message Signatures allows sub-portions of the HTTP message to be signed, it is possible for two different HTTP messages to validate against the same signature. The most extreme form of this would be a signature over no message components. If such a signature were intercepted, it could be replayed at will by an attacker, attached to any HTTP message. Even with sufficient component coverage, a given signature could be applied to two similar HTTP messages, allowing a message to be replayed by an attacker with the signature intact.

To counteract these kinds of attacks, it's first important for the signer to cover sufficient portions of the message to differentiate it from other messages. In addition, the signature can use the `nonce` signature parameter to provide a per-message unique value to allow the verifier to detect replay of the signature itself if a nonce value is repeated. Furthermore, the signer can provide a timestamp for when the signature was created and a time at which the signer considers the signature to be invalid, limiting the utility of a captured signature value.

If a verifier wants to trigger a new signature from a signer, it can send the `Accept-Signature` header field with a new `nonce` parameter. An attacker that is simply replaying a signature would not be able to generate a new signature with the chosen nonce value.

## Insufficient Coverage {#security-coverage}

Any portions of the message not covered by the signature are susceptible to modification by an attacker without affecting the signature. An attacker can take advantage of this by introducing a header field or other message component that will change the processing of the message but will not be covered by the signature. Such an altered message would still pass signature verification, but when the verifier processes the message as a whole, the unsigned content injected by the attacker would subvert the trust conveyed by the valid signature and change the outcome of processing the message.

To combat this, an application of this specification should require as much of the message as possible to be signed, within the limits of the application and deployment. The verifier should only trust message components that have been signed. Verifiers could also strip out any sensitive unsigned portions of the message before processing of the message continues.

## Cryptography and Signature Collision {#security-collision}

The HTTP Message Signatures specification does not define any of its own cryptographic primitives, and instead relies on other specifications to define such elements. If the signature algorithm or key used to process the signature input string is vulnerable to any attacks, the resulting signature will also be susceptible to these same attacks.

A common attack against signature systems is to force a signature collision, where the same signature value successfully verifies against multiple different inputs. Since this specification relies on reconstruction of the input string based on an HTTP message, and the list of components signed is fixed in the signature, it is difficult but not impossible for an attacker to effect such a collision. An attacker would need to manipulate the HTTP message and its covered message components in order to make the collision effective.

To counter this, only vetted keys and signature algorithms should be used to sign HTTP messages. The HTTP Message Signatures Algorithm Registry is one source of potential trusted algorithms.

While it is possible for an attacker to substitute the signature parameters value or the signature value separately, the [signature input generation algorithm](#create-sig-input) always covers the signature parameters as the final value in the input string using a deterministic serialization method. This step strongly binds the signature input with the signature value in a way that makes it much more difficult for an attacker to perform a partial substitution on the signature inputs.

## Key Theft {#security-keys}

A foundational assumption of signature-based cryptographic systems is that the signing key is not compromised by an attacker. If the keys used to sign the message are exfiltrated or stolen, the attacker will be able to generate their own signatures using those keys. As a consequence, signers have to protect any signing key material from exfiltration, capture, and use by an attacker.

To combat this, signers can rotate keys over time to limit the amount of time stolen keys are useful. Signers can also use key escrow and storage systems to limit the attack surface against keys. Furthermore, the use of asymmetric signing algorithms exposes key material less than the use of [symmetric signing algorithms](#security-symmetric).

## Modification of Required Message Parameters {#security-modify}

An attacker could effectively deny a service by modifying an otherwise benign signature parameter or signed message component. While rejecting a modified message is the desired behavior, consistently failing signatures could lead to the verifier turning off signature checking in order to make systems work again (see {{security-ignore}}).

If such failures are common within an application, the signer and verifier should compare their generated signature input strings with each other to determine which part of the message is being modified. However, the signer and verifier should not remove the requirement to sign the modified component when it is suspected an attacker is modifying the component.

## Mismatch of Signature Parameters from Message {#security-mismatch}

The verifier needs to make sure that the signed message components match those in the message itself. This specification encourages this by requiring the verifier to derive these values from the message, but lazy cacheing or conveyance of the signature input string to a processing system could lead to downstream verifiers accepting a message that does not match the presented signature.

## Multiple Signature Confusion {#security-multiple}

Since [multiple signatures can be applied to one message](#signature-multiple), it is possible for an attacker to attach their own signature to a captured message without modifying existing signatures. This new signature could be completely valid based on the attacker's key, or it could be an invalid signature for any number of reasons. Each of these situations need to be accounted for.

A verifier processing a set of valid signatures needs to account for all of the signers, identified by the signing keys. Only signatures from expected signers should be accepted, regardless of the cryptographic validity of the signature itself.

A verifier processing a set of signatures on a message also needs to determine what to do when one or more of the signatures are not valid. If a message is accepted when at least one signature is valid, then a verifier could drop all invalid signatures from the request before processing the message further. Alternatively, if the verifier rejects a message for a single invalid signature, an attacker could use this to deny service to otherwise valid messages by injecting invalid signatures alongside the valid ones.

## Signature Labels {#security-labels}

HTTP Message Signature values are identified in the `Signature` and `Signature-Input` field values by unique labels. These labels are chosen only when attaching the signature values to the message and are not accounted for in the signing process. An intermediary adding its own signature is allowed to re-label an existing signature when processing the message.

Therefore, applications should not rely on specific labels being present, and applications should not put semantic meaning on the labels themselves. Instead, additional signature parmeters can be used to convey whatever additional meaning is required to be attached to and covered by the signature.

## Symmetric Cryptography {#security-symmetric}

The HTTP Message Signatures specification allows for both asymmetric and symmetric cryptography to be applied to HTTP messages. By its nature, symmetric cryptographic methods require the same key material to be known by both the signer and verifier. This effectively means that a verifier is capable of generating a valid signature, since they have access to the same key material. An attacker that is able to compromise a verifier would be able to then impersonate a signer.

Where possible, asymmetric methods or secure key agreement mechanisms should be used in order to avoid this type of attack. When symmetric methods are used, distribution of the key material needs to be protected by the overall system. One technique for this is the use of separate cryptographic modules that separate the verification process (and therefore the key material) from other code, minimizing the vulnerable attack surface. Another technique is the use of key derivation functions that allow the signer and verifier to agree on unique keys for each message without having to share the key values directly.

Additionally, if symmetric algorithms are allowed within a system, special care must be taken to avoid [key downgrade attacks](#security-keydowngrade).

## Canonicalization Attacks {#security-canonicalization}

Any ambiguity in the generation of the signature input string could provide an attacker with leverage to substitute or break a signature on a message. Some message component values, particularly HTTP field values, are potentially susceptible to broken implementations that could lead to unexpected and insecure behavior. Naive implementations of this specification might implement HTTP field processing by taking the single value of a field and using it as the direct component value without processing it appropriately.

For example, if the handling of `obs-fold` field values does not remove the internal line folding and whitespace, additional newlines could be introduced into the signature input string by the signer, providing a potential place for an attacker to mount a [signature collision](#security-collision) attack. Alternatively, if header fields that appear multiple times are not joined into a single string value, as is required by this specification, similar attacks can be mounted as a signed component value would show up in the input string more than once and could be substituted or otherwise attacked in this way.

To counter this, the entire field processing algorithm needs to be implemented by all implementations of signers and verifiers.

## Key Specification Mix-Up {#security-keymixup}

The existence of a valid signature on an HTTP message is not sufficient to prove that the message has been signed by the appropriate party. It is up to the verifier to ensure that a given key and algorithm are appropriate for the message in question. If the verifier does not perform such a step, an attacker could substitute their own signature using their own key on a message and force a verifier to accept and process it. To combat this, the verifier needs to ensure that not only does the signature validate for a message, but that the key and algorithm used are appropriate.

## HTTP Versions and Component Ambiguity {#security-versions}

Some message components are expressed in different ways across HTTP versions. For example, the authority of the request target is sent using the `Host` header field in HTTP 1.1 but with the `:authority` pseudo-header in HTTP 2. If a signer sends an HTTP 1.1 message and signs the `Host` field, but the message is translated to HTTP 2 before it reaches the verifier, the signature will not validate as the `Host` header field could be dropped.

It is for this reason that HTTP Message Signatures defines a set of derived components that define a single way to get value in question, such as the `@authority` derived component identifier ({{content-request-authority}}) in lieu of the `Host` header field. Applications should therefore prefer derived component identifiers for such options where possible.

## Key and Algorithm Specification Downgrades {#security-keydowngrade}

Applications of this specification need to protect against key specification downgrade attacks. For example, the same RSA key can be used for both RSA-PSS and RSA v1.5 signatures. If an application expects a key to only be used with RSA-PSS, it needs to reject signatures for that key using the weaker RSA 1.5 specification.

Another example of a downgrade attack occurs when an asymmetric algorithm is expected, such as RSA-PSS, but an attacker substitutes a signature using symmetric algorithm, such as HMAC. A naive verifier implementation could use the value of the public RSA key as the input to the HMAC verification function. Since the public key is known to the attacker, this would allow the attacker to create a valid HMAC signature against this known key. To prevent this, the verifier needs to ensure that both the key material and the algorithm are appropriate for the usage in question. Additionally, while this specification does allow runtime specification of the algorithm using the `alg` signature parameter, applications are encouraged to use other mechanisms such as static configuration or higher protocol-level algorithm specification instead.

## Parsing Structured Field Values {#security-structured}

Several parts of this specification rely on the parsing of structured field values {{RFC8941}}. In particular, [normalization of HTTP structured field values](#http-header-structured), [referencing members of a dictionary structured field](#http-header-dictionary), and processing the `@signature-input` value when [verifying a signature](#verify). While structured field values are designed to be relatively simple to parse, a naive or broken implementation of such a parser could lead to subtle attack surfaces being exposed in the implementation.

For example, if a buggy parser of the `@signature-input` value does not enforce proper closing of quotes around string values within the list of component identifiers, an attacker could take advantage of this and inject additional content into the signature input string through manipulating the `Signature-Input` field value on a message.

To counteract this, implementations should use fully compliant and trusted parsers for all structured field processing, both on the signer and verifier side.

## Choosing Message Components {#security-components}

Applications of HTTP Message Signatures need to decide which message components will be covered by the signature. Depending on the application, some components could be expected to be changed by intermediaries prior to the signature's verification. If these components are covered, such changes would, by design, break the signature.

However, the HTTP Message Signature standard allows for flexibility in determining which components are signed precisely so that a given application can choose the appropriate portions of the message that need to be signed, avoiding problematic components. For example, a web application framework that relies on rewriting query parameters might avoid use of the `@query` content identifier in favor of sub-indexing the query value using `@query-params` content identifier instead.

Some components are expected to be changed by intermediaries and ought not to be signed under most circumstance. The `Via` and `Forwarded` header fields, for example, are expected to be manipulated by proxies and other middle-boxes, including replacing or entirely dropping existing values. These fields should not be covered by the signature except in very limited and tightly-coupled scenarios.

Additional considerations for choosing signature aspects are discussed in {{application}}.

## Confusing HTTP Field Names for Derived Component Identifiers {#security-lazy-header-parser}

The definition of HTTP field names does not allow for the use of the `@` character anywhere in the name. As such, since all derived component identifiers start with the `@` character, these namespaces should be completely separate. However, some HTTP implementations are not sufficiently strict about the characters accepted in HTTP headers. In such implementations, a sender (or attacker) could inject a header field starting with an `@` character and have it passed through to the application code. These invalid header fields could be used to override a portion of the derived message content and substitute an arbitrary value, providing a potential place for an attacker to mount a [signature collision](#security-collision) attack.

To combat this, when selecting values for a message component, if the component identifier starts with the `@` character, it needs to be processed as a derived component and never taken as a fields. Only if the component identifier does not start with the `@` character can it be taken from the fields of the message. The algorithm discussed in {{create-sig-input}} provides a safe order of operations.

## Non-deterministic Signature Primitives {#security-nondeterministic}

Some cryptographic primitives such as RSA PSS and ECDSA have non-deterministic outputs, which include some amount of entropy within the algorithm. For such algorithms, multiple signatures generated in succession will not match. A lazy implementation of a verifier could ignore this distinction and simply check for the same value being created by re-signing the signature input. Such an implementation would work for deterministic algorithms such as HMAC and EdDSA but fail to verify valid signatures made using non-deterministic algorithms. It is therefore important that a verifier always use the correctly-defined verification function for the algorithm in question and not do a simple comparison.

## Choosing Signature Parameters and Derived Components over HTTP Fields {#security-not-fields}

Some HTTP fields have values and interpretations that are similar to HTTP signature parameters or derived components. In most cases, it is more desirable to sign the non-field alternative. In particular, the following fields should usually not be included in the signature unless the application specifically requires it:

"date"
: The "date" field value represents the timestamp of the HTTP message. However, the creation time of the signature itself is encoded in the `created` signature parameter. These two values can be different, depending on how the signature and the HTTP message are created and serialized. Applications processing signatures for valid time windows should use the `created` signature parameter for such calculations. An application could also put limits on how much skew there is between the "date" field and the `created` signature parameter, in order to limit the application of a generated signature to different HTTP messages. See also {{security-replay}} and {{security-coverage}}.

"host"
: The "host" header field is specific to HTTP 1.1, and its functionality is subsumed by the "@authority" derived component, defined in {{content-request-authority}}. In order to preserve the value across different HTTP versions, applications should always use the "@authority" derived component.

# Privacy Considerations {#privacy}

## Identification through Keys {#privacy-identify-keys}

If a signer uses the same key with multiple verifiers, or uses the same key over time with a single verifier, the ongoing use of that key can be used to track the signer throughout the set of verifiers that messages are sent to. Since cryptographic keys are meant to be functionally unique, the use of the same key over time is a strong indicator that it is the same party signing multiple messages.

In many applications, this is a desirable trait, and it allows HTTP Message Signatures to be used as part of authenticating the signer to the verifier. However, unintentional tracking that a signer might not be aware of. To counter this kind of tracking, a signer can use a different key for each verifier that it is in communication with. Sometimes, a signer could also rotate their key when sending messages to a given verifier. These approaches do not negate the need for other anti-tracking techniques to be applied as necessary.

## Signatures do not provide confidentiality {#privacy-confidentiality}

HTTP Message Signatures do not provide confidentiality of any of the information protected by the signature. The content of the HTTP message, including the value of all fields and the value of the signature itself, is presented in plaintext to any party with access to the message.

To provide confidentiality at the transport level, TLS or its equivalent can be used as discussed in {{security-tls}}.

## Oracles {#privacy-oracle}

It is important to balance the need for providing useful feedback to developers on error conditions without providing additional information to an attacker. For example, a naive but helpful server implementation might try to indicate the required key identifier needed for requesting a resource. If someone knows who controls that key, a correlation can be made between the resource's existence and the party identified by the key. Access to such information could be used by an attacker as a means to target the legitimate owner of the resource for further attacks.

## Required Content {#privacy-required}

A core design tenet of this specification is that all message components covered by the signature need to be available to the verifier in order to recreate the signature input string and verify the signature. As a consequence, if an application of this specification requires that a particular field be signed, the verifier will need access to the value of that field.

For example, in some complex systems with intermediary processors this could cause the surprising behavior of an intermediary not being able to remove privacy-sensitive information from a message before forwarding it on for processing, for fear of breaking the signature. A possible mitigation for this specific situation would be for the intermediary to verify the signature itself, then modifying the message to remove the privacy-sensitive information. The intermediary can add its own signature at this point to signal to the next destination that the incoming signature was validated, as is shown in the example in {{signature-multiple}}.

--- back

# Detecting HTTP Message Signatures {#detection}

There have been many attempts to create signed HTTP messages in the past, including other non-standardized definitions of the `Signature` field, which is used within this specification. It is recommended that developers wishing to support both this specification and other historical drafts do so carefully and deliberately, as incompatibilities between this specification and various versions of other drafts could lead to unexpected problems.

It is recommended that implementers first detect and validate the `Signature-Input` field defined in this specification to detect that this standard is in use and not an alternative. If the `Signature-Input` field is present, all `Signature` fields can be parsed and interpreted in the context of this draft.

# Examples

The following non-normative examples are provided as a means of testing implementations of HTTP Message Signatures. The signed messages given can be used to create the signature input strings with the stated parameters, creating signatures using the stated algorithms and keys.

The private keys given can be used to generate signatures, though since several of the demonstrated algorithms are nondeterministic, the results of a signature are expected to be different from the exact bytes of the examples. The public keys given can be used to validate all signed examples.

## Example Keys {#example-keys}

This section provides cryptographic keys that are referenced in example signatures throughout this document.  These keys MUST NOT be used for any purpose other than testing.

The key identifiers for each key are used throughout the examples in this specification. It is assumed for these examples that the signer and verifier can unambiguously dereference all key identifiers used here, and that the keys and algorithms used are appropriate for the context in which the signature is presented.

The components for each private key in PEM format can be displayed by executing the following OpenSSL command:

~~~
openssl pkey -text
~~~

This command was tested with all the example keys on OpenSSL version 1.1.1m. Note that some systems cannot produce or use these keys directly, and may require additional processing.

### Example Key RSA test {#example-key-rsa-test}

The following key is a 2048-bit RSA public and private key pair, referred to in this document
as `test-key-rsa`. This key is encoded in PEM Format, with no encryption.

~~~
-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEAhAKYdtoeoy8zcAcR874L8cnZxKzAGwd7v36APp7Pv6Q2jdsPBRrw
WEBnez6d0UDKDwGbc6nxfEXAy5mbhgajzrw3MOEt8uA5txSKobBpKDeBLOsdJKFq
MGmXCQvEG7YemcxDTRPxAleIAgYYRjTSd/QBwVW9OwNFhekro3RtlinV0a75jfZg
kne/YiktSvLG34lw2zqXBDTC5NHROUqGTlML4PlNZS5Ri2U4aCNx2rUPRcKIlE0P
uKxI4T+HIaFpv8+rdV6eUgOrB2xeI1dSFFn/nnv5OoZJEIB+VmuKn3DCUcCZSFlQ
PSXSfBDiUGhwOw76WuSSsf1D4b/vLoJ10wIDAQAB
-----END RSA PUBLIC KEY-----

-----BEGIN RSA PRIVATE KEY-----
MIIEqAIBAAKCAQEAhAKYdtoeoy8zcAcR874L8cnZxKzAGwd7v36APp7Pv6Q2jdsP
BRrwWEBnez6d0UDKDwGbc6nxfEXAy5mbhgajzrw3MOEt8uA5txSKobBpKDeBLOsd
JKFqMGmXCQvEG7YemcxDTRPxAleIAgYYRjTSd/QBwVW9OwNFhekro3RtlinV0a75
jfZgkne/YiktSvLG34lw2zqXBDTC5NHROUqGTlML4PlNZS5Ri2U4aCNx2rUPRcKI
lE0PuKxI4T+HIaFpv8+rdV6eUgOrB2xeI1dSFFn/nnv5OoZJEIB+VmuKn3DCUcCZ
SFlQPSXSfBDiUGhwOw76WuSSsf1D4b/vLoJ10wIDAQABAoIBAG/JZuSWdoVHbi56
vjgCgkjg3lkO1KrO3nrdm6nrgA9P9qaPjxuKoWaKO1cBQlE1pSWp/cKncYgD5WxE
CpAnRUXG2pG4zdkzCYzAh1i+c34L6oZoHsirK6oNcEnHveydfzJL5934egm6p8DW
+m1RQ70yUt4uRc0YSor+q1LGJvGQHReF0WmJBZHrhz5e63Pq7lE0gIwuBqL8SMaA
yRXtK+JGxZpImTq+NHvEWWCu09SCq0r838ceQI55SvzmTkwqtC+8AT2zFviMZkKR
Qo6SPsrqItxZWRty2izawTF0Bf5S2VAx7O+6t3wBsQ1sLptoSgX3QblELY5asI0J
YFz7LJECgYkAsqeUJmqXE3LP8tYoIjMIAKiTm9o6psPlc8CrLI9CH0UbuaA2JCOM
cCNq8SyYbTqgnWlB9ZfcAm/cFpA8tYci9m5vYK8HNxQr+8FS3Qo8N9RJ8d0U5Csw
DzMYfRghAfUGwmlWj5hp1pQzAuhwbOXFtxKHVsMPhz1IBtF9Y8jvgqgYHLbmyiu1
mwJ5AL0pYF0G7x81prlARURwHo0Yf52kEw1dxpx+JXER7hQRWQki5/NsUEtv+8RT
qn2m6qte5DXLyn83b1qRscSdnCCwKtKWUug5q2ZbwVOCJCtmRwmnP131lWRYfj67
B/xJ1ZA6X3GEf4sNReNAtaucPEelgR2nsN0gKQKBiGoqHWbK1qYvBxX2X3kbPDkv
9C+celgZd2PW7aGYLCHq7nPbmfDV0yHcWjOhXZ8jRMjmANVR/eLQ2EfsRLdW69bn
f3ZD7JS1fwGnO3exGmHO3HZG+6AvberKYVYNHahNFEw5TsAcQWDLRpkGybBcxqZo
81YCqlqidwfeO5YtlO7etx1xLyqa2NsCeG9A86UjG+aeNnXEIDk1PDK+EuiThIUa
/2IxKzJKWl1BKr2d4xAfR0ZnEYuRrbeDQYgTImOlfW6/GuYIxKYgEKCFHFqJATAG
IxHrq1PDOiSwXd2GmVVYyEmhZnbcp8CxaEMQoevxAta0ssMK3w6UsDtvUvYvF22m
qQKBiD5GwESzsFPy3Ga0MvZpn3D6EJQLgsnrtUPZx+z2Ep2x0xc5orneB5fGyF1P
WtP+fG5Q6Dpdz3LRfm+KwBCWFKQjg7uTxcjerhBWEYPmEMKYwTJF5PBG9/ddvHLQ
EQeNC8fHGg4UXU8mhHnSBt3EA10qQJfRDs15M38eG2cYwB1PZpDHScDnDA0=
-----END RSA PRIVATE KEY-----
~~~

### Example RSA PSS Key {#example-key-rsa-pss-test}

The following key is a 2048-bit RSA public and private key pair, referred to in this document
as `test-key-rsa-pss`. This key is PCKS#8 encoded in PEM format, with no encryption.

~~~
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAr4tmm3r20Wd/PbqvP1s2
+QEtvpuRaV8Yq40gjUR8y2Rjxa6dpG2GXHbPfvMs8ct+Lh1GH45x28Rw3Ry53mm+
oAXjyQ86OnDkZ5N8lYbggD4O3w6M6pAvLkhk95AndTrifbIFPNU8PPMO7OyrFAHq
gDsznjPFmTOtCEcN2Z1FpWgchwuYLPL+Wokqltd11nqqzi+bJ9cvSKADYdUAAN5W
Utzdpiy6LbTgSxP7ociU4Tn0g5I6aDZJ7A8Lzo0KSyZYoA485mqcO0GVAdVw9lq4
aOT9v6d+nb4bnNkQVklLQ3fVAvJm+xdDOp9LCNCN48V2pnDOkFV6+U9nV5oyc6XI
2wIDAQAB
-----END PUBLIC KEY-----

-----BEGIN PRIVATE KEY-----
MIIEvgIBADALBgkqhkiG9w0BAQoEggSqMIIEpgIBAAKCAQEAr4tmm3r20Wd/Pbqv
P1s2+QEtvpuRaV8Yq40gjUR8y2Rjxa6dpG2GXHbPfvMs8ct+Lh1GH45x28Rw3Ry5
3mm+oAXjyQ86OnDkZ5N8lYbggD4O3w6M6pAvLkhk95AndTrifbIFPNU8PPMO7Oyr
FAHqgDsznjPFmTOtCEcN2Z1FpWgchwuYLPL+Wokqltd11nqqzi+bJ9cvSKADYdUA
AN5WUtzdpiy6LbTgSxP7ociU4Tn0g5I6aDZJ7A8Lzo0KSyZYoA485mqcO0GVAdVw
9lq4aOT9v6d+nb4bnNkQVklLQ3fVAvJm+xdDOp9LCNCN48V2pnDOkFV6+U9nV5oy
c6XI2wIDAQABAoIBAQCUB8ip+kJiiZVKF8AqfB/aUP0jTAqOQewK1kKJ/iQCXBCq
pbo360gvdt05H5VZ/RDVkEgO2k73VSsbulqezKs8RFs2tEmU+JgTI9MeQJPWcP6X
aKy6LIYs0E2cWgp8GADgoBs8llBq0UhX0KffglIeek3n7Z6Gt4YFge2TAcW2WbN4
XfK7lupFyo6HHyWRiYHMMARQXLJeOSdTn5aMBP0PO4bQyk5ORxTUSeOciPJUFktQ
HkvGbym7KryEfwH8Tks0L7WhzyP60PL3xS9FNOJi9m+zztwYIXGDQuKM2GDsITeD
2mI2oHoPMyAD0wdI7BwSVW18p1h+jgfc4dlexKYRAoGBAOVfuiEiOchGghV5vn5N
RDNscAFnpHj1QgMr6/UG05RTgmcLfVsI1I4bSkbrIuVKviGGf7atlkROALOG/xRx
DLadgBEeNyHL5lz6ihQaFJLVQ0u3U4SB67J0YtVO3R6lXcIjBDHuY8SjYJ7Ci6Z6
vuDcoaEujnlrtUhaMxvSfcUJAoGBAMPsCHXte1uWNAqYad2WdLjPDlKtQJK1diCm
rqmB2g8QE99hDOHItjDBEdpyFBKOIP+NpVtM2KLhRajjcL9Ph8jrID6XUqikQuVi
4J9FV2m42jXMuioTT13idAILanYg8D3idvy/3isDVkON0X3UAVKrgMEne0hJpkPL
FYqgetvDAoGBAKLQ6JZMbSe0pPIJkSamQhsehgL5Rs51iX4m1z7+sYFAJfhvN3Q/
OGIHDRp6HjMUcxHpHw7U+S1TETxePwKLnLKj6hw8jnX2/nZRgWHzgVcY+sPsReRx
NJVf+Cfh6yOtznfX00p+JWOXdSY8glSSHJwRAMog+hFGW1AYdt7w80XBAoGBAImR
NUugqapgaEA8TrFxkJmngXYaAqpA0iYRA7kv3S4QavPBUGtFJHBNULzitydkNtVZ
3w6hgce0h9YThTo/nKc+OZDZbgfN9s7cQ75x0PQCAO4fx2P91Q+mDzDUVTeG30mE
t2m3S0dGe47JiJxifV9P3wNBNrZGSIF3mrORBVNDAoGBAI0QKn2Iv7Sgo4T/XjND
dl2kZTXqGAk8dOhpUiw/HdM3OGWbhHj2NdCzBliOmPyQtAr770GITWvbAI+IRYyF
S7Fnk6ZVVVHsxjtaHy1uJGFlaZzKR4AGNaUTOJMs6NadzCmGPAxNQQOCqoUjn4XR
rOjr9w349JooGXhOxbu8nOxX
-----END PRIVATE KEY-----
~~~

### Example ECC P-256 Test Key {#example-key-ecc-p256}

The following key is a public and private elliptical curve key pair over the curve P-256, referred
to in this document as `test-key-ecc-p256. This key is encoded in PEM format, with no encryption.

~~~
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEqIVYZVLCrPZHGHjP17CTW0/+D9Lf
w0EkjqF7xB4FivAxzic30tMM4GF+hR6Dxh71Z50VGGdldkkDXZCnTNnoXQ==
-----END PUBLIC KEY-----

-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIFKbhfNZfpDsW43+0+JjUr9K+bTeuxopu653+hBaXGA7oAoGCCqGSM49
AwEHoUQDQgAEqIVYZVLCrPZHGHjP17CTW0/+D9Lfw0EkjqF7xB4FivAxzic30tMM
4GF+hR6Dxh71Z50VGGdldkkDXZCnTNnoXQ==
-----END EC PRIVATE KEY-----
~~~

### Example Ed25519 Test Key {#example-key-ed25519}

The following key is an elliptical curve key over the Edwards curve ed25519, referred to in this document as `test-key-edd25519`. This key is PCKS#8 encoded in PEM format, with no encryption.

~~~
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAJrQLj5P/89iXES9+vFgrIy29clF9CC/oPPsw3c5D0bs=
-----END PUBLIC KEY-----

-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIJ+DYvh6SEqVTm50DFtMDoQikTmiCqirVv9mWG9qfSnF
-----END PRIVATE KEY-----
~~~

### Example Shared Secret {#example-shared-secret}

The following shared secret is 64 randomly-generated bytes encoded in Base64,
referred to in this document as `test-shared-secret`.

~~~
NOTE: '\' line wrapping per RFC 8792

uzvJfB4u3N0Jy4T7NZ75MDVcr8zSTInedJtkgcu46YW4XByzNJjxBdtjUkdJPBt\
  bmHhIDi6pcl8jsasjlTMtDQ==
~~~

## Test Cases

This section provides non-normative examples that may be used as test cases to validate implementation correctness. These examples are based on the following HTTP messages:

For requests, this `test-request` message is used:

~~~ http-message
POST /foo?param=Value&Pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18

{"hello": "world"}
~~~

For responses, this `test-response` message is used:

~~~ http-message
HTTP/1.1 200 OK
Date: Tue, 20 Apr 2021 02:07:56 GMT
Content-Type: application/json
Content-Digest: sha-512=:JlEy2bfUz7WrWIjc1qV6KVLpdr/7L5/L4h7Sxvh6sN\
  HpDQWDCL+GauFQWcZBvVDhiyOnAQsxzZFYwi0wDH+1pw==:
Content-Length: 23

{"message": "good dog"}
~~~

### Minimal Signature Using rsa-pss-sha512

This example presents a minimal signature using the `rsa-pss-sha512` algorithm over `test-request`, covering none
of the components of the HTTP message, but providing a timestamped signature proof of possession of the key with a signer-provided nonce.

The corresponding signature input is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@signature-params": ();created=1618884473;keyid="test-key-rsa-pss"\
  ;nonce="b3k2pp5k7z-50gnwp.yemd"
~~~

This results in the following `Signature-Input` and `Signature` headers being added to the message under the signature label `sig-b21`:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b21=();created=1618884473\
  ;keyid="test-key-rsa-pss";nonce="b3k2pp5k7z-50gnwp.yemd"
Signature: sig-b21=:d2pmTvmbncD3xQm8E9ZV2828BjQWGgiwAaw5bAkgibUopem\
  LJcWDy/lkbbHAve4cRAtx31Iq786U7it++wgGxbtRxf8Udx7zFZsckzXaJMkA7ChG\
  52eSkFxykJeNqsrWH5S+oxNFlD4dzVuwe8DhTSja8xxbR/Z2cOGdCbzR72rgFWhzx\
  2VjBqJzsPLMIQKhO4DGezXehhWwE56YCE+O6c0mKZsfxVrogUvA4HELjVKWmAvtl6\
  UnCh8jYzuVG5WSb/QEVPnP5TmcAnLH1g+s++v6d4s8m0gCw1fV5/SITLq9mhho8K3\
  +7EPYTU8IU1bLhdxO5Nyt8C8ssinQ98Xw9Q==:
~~~

Note that since the covered components list is empty, this signature could be applied by an attacker to an unrelated HTTP message. In this example, the `nonce` parameter is included to prevent the same signature from being replayed more than once, but if an attacker intercepts the signature and prevents its delivery to the verifier, the attacker could apply this signature to another message. Therefore, use of an empty covered components set is discouraged. See {{security-coverage}} for more discussion.

Note that the RSA PSS algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

### Selective Covered Components using rsa-pss-sha512

This example covers additional components in `test-request` using the `rsa-pss-sha512` algorithm.

The corresponding signature input is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@authority": example.com
"content-digest": sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX\
  +TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
"@signature-params": ("@authority" "content-digest")\
  ;created=1618884473;keyid="test-key-rsa-pss"
~~~


This results in the following `Signature-Input` and `Signature` headers being added to the message under the label `sig-b22`:


~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b22=("@authority" "content-digest")\
  ;created=1618884473;keyid="test-key-rsa-pss"
Signature: sig-b22=:Fee1uy9YGZq5UUwwYU6vz4dZNvfw3GYrFl1L6YlVIyUMuWs\
  wWDNSvql4dVtSeidYjYZUm7SBCENIb5KYy2ByoC3bI+7gydd2i4OAT5lyDtmeapnA\
  a8uP/b9xUpg+VSPElbBs6JWBIQsd+nMdHDe+ls/IwVMwXktC37SqsnbNyhNp6kcvc\
  WpevjzFcD2VqdZleUz4jN7P+W5A3wHiMGfIjIWn36KXNB+RKyrlGnIS8yaBBrom5r\
  cZWLrLbtg6VlrH1+/07RV+kgTh/l10h8qgpl9zQHu7mWbDKTq0tJ8K4ywcPoC4s2I\
  4rU88jzDKDGdTTQFZoTVZxZmuTM1FvHfzIw==:
~~~

Note that the RSA PSS algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

### Full Coverage using rsa-pss-sha512

This example covers all applicable in `test-request` (including the content type and length) plus many derived components, again using the `rsa-pss-sha512` algorithm. Note that the `Host` header field is not covered because the `@authority` derived component is included instead.

The corresponding signature input is:

~~~
NOTE: '\' line wrapping per RFC 8792

"date": Tue, 20 Apr 2021 02:07:55 GMT
"@method": POST
"@path": /foo
"@query": ?param=Value&Pet=dog
"@authority": example.com
"content-type": application/json
"content-digest": sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX\
  +TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
"content-length": 18
"@signature-params": ("date" "@method" "@path" "@query" \
  "@authority" "content-type" "content-digest" "content-length")\
  ;created=1618884473;keyid="test-key-rsa-pss"
~~~

This results in the following `Signature-Input` and `Signature` headers being added to the message under the label `sig-b23`:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b23=("date" "@method" "@path" "@query" \
  "@authority" "content-type" "content-digest" "content-length")\
  ;created=1618884473;keyid="test-key-rsa-pss"
Signature: sig-b23=:bbN8oArOxYoyylQQUU6QYwrTuaxLwjAC9fbY2F6SVWvh0yB\
  iMIRGOnMYwZ/5MR6fb0Kh1rIRASVxFkeGt683+qRpRRU5p2voTp768ZrCUb38K0fU\
  xN0O0iC59DzYx8DFll5GmydPxSmme9v6ULbMFkl+V5B1TP/yPViV7KsLNmvKiLJH1\
  pFkh/aYA2HXXZzNBXmIkoQoLd7YfW91kE9o/CCoC1xMy7JA1ipwvKvfrs65ldmlu9\
  bpG6A9BmzhuzF8Eim5f8ui9eH8LZH896+QIF61ka39VBrohr9iyMUJpvRX2Zbhl5Z\
  JzSRxpJyoEZAFL2FUo5fTIztsDZKEgM4cUA==:
~~~

Note in this example that the value of the `Date` header and the value of the `created` signature parameter need not be the same. This is due to the fact that the `Date` header is added when creating the HTTP Message and the `created` parameter is populated when creating the signature over that message, and these two times could vary. If the `Date` header is covered by the signature, it is up to the verifier to determine whether its value has to match that of the `created` parameter or not. See {{security-not-fields}} for more discussion.

Note that the RSA PSS algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

### Signing a Response using ecdsa-p256-sha256

This example covers portions of the `test-response` response message using the `ecdsa-p256-sha256` algorithm
and the key `test-key-ecc-p256`.

The corresponding signature input is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@status": 200
"content-type": application/json
"content-digest": sha-512=:JlEy2bfUz7WrWIjc1qV6KVLpdr/7L5/L4h7Sxvh6\
  sNHpDQWDCL+GauFQWcZBvVDhiyOnAQsxzZFYwi0wDH+1pw==:
"content-length": 23
"@signature-params": ("@status" "content-type" "content-digest" \
  "content-length");created=1618884473;keyid="test-key-ecc-p256"
~~~

This results in the following `Signature-Input` and `Signature` headers being added to the message under the label `sig-b24`:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b24=("@status" "content-type" \
  "content-digest" "content-length");created=1618884473\
  ;keyid="test-key-ecc-p256"
Signature: sig-b24=:0Ry6HsvzS5VmA6HlfBYS/fYYeNs7fYuA7s0tAdxfUlPGv0C\
  SVuwrrzBOjcCFHTxVRJ01wjvSzM2BetJauj8dsw==:
~~~

Note that the ECDSA algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

### Signing a Request using hmac-sha256

This example covers portions of the `test-request` using the `hmac-sha256` algorithm and the
secret `test-shared-secret`.

The corresponding signature input is:

~~~
NOTE: '\' line wrapping per RFC 8792

"date": Tue, 20 Apr 2021 02:07:55 GMT
"@authority": example.com
"content-type": application/json
"@signature-params": ("date" "@authority" "content-type")\
  ;created=1618884473;keyid="test-shared-secret"
~~~

This results in the following `Signature-Input` and `Signature` headers being added to the message under the label `sig-b25`:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b25=("date" "@authority" "content-type")\
  ;created=1618884473;keyid="test-shared-secret"
Signature: sig-b25=:pxcQw6G3AjtMBQjwo8XzkZf/bws5LelbaMk5rGIGtE8=:
~~~

Before using symmetric signatures in practice, see the discussion of the security tradeoffs in {{security-symmetric}}.

### Signing a Request using ed25519

This example covers portions of the `test-request` using the `ed25519` algorithm
and the key `test-key-ed25519`.

The corresponding signature input is:

~~~
NOTE: '\' line wrapping per RFC 8792

"date": Tue, 20 Apr 2021 02:07:55 GMT
"@method": POST
"@path": /foo
"@authority": example.com
"content-type": application/json
"content-length": 18
"@signature-params": ("date" "@method" "@path" "@authority" \
  "content-type" "content-length");created=1618884473\
  ;keyid="test-key-ed25519"
~~~

This results in the following `Signature-Input` and `Signature` headers being added to the message under the label `sig-b26`:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b26=("date" "@method" "@path" "@authority" \
  "content-type" "content-length");created=1618884473\
  ;keyid="test-key-ed25519"
Signature: sig-b26=:wqcAqbmYJ2ji2glfAMaRy4gruYYnx2nEFN2HN6jrnDnQCK1\
  u02Gb04v9EDgwUPiu4A0w6vuQv5lIp5WPpBKRCw==:
~~~

## TLS-Terminating Proxies

In this example, there is a TLS-terminating reverse proxy sitting in front of the resource. The client does not sign the request but instead uses mutual TLS to make its call. The terminating proxy validates the TLS stream and injects a `Client-Cert` header according to {{I-D.ietf-httpbis-client-cert-field}}, and then applies a signature to this field. By signing this header field, a reverse proxy can not only attest to its own validation of the initial request's TLS parameters but also authenticate itself to the backend system independently of the client's actions.

The client makes the following request to the TLS terminating proxy using mutual TLS:

~~~ http-message
POST /foo?param=Value&Pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Length: 18

{"hello": "world"}
~~~

The proxy processes the TLS connection and extracts the client's TLS certificate to a `Client-Cert` header field and passes it along to the internal service hosted at `service.internal.example`. This results in the following unsigned request:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: service.internal.example
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Length: 18
Client-Cert: :MIIBqDCCAU6gAwIBAgIBBzAKBggqhkjOPQQDAjA6MRswGQYDVQQKD\
  BJMZXQncyBBdXRoZW50aWNhdGUxGzAZBgNVBAMMEkxBIEludGVybWVkaWF0ZSBDQT\
  AeFw0yMDAxMTQyMjU1MzNaFw0yMTAxMjMyMjU1MzNaMA0xCzAJBgNVBAMMAkJDMFk\
  wEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE8YnXXfaUgmnMtOXU/IncWalRhebrXmck\
  C8vdgJ1p5Be5F/3YC8OthxM4+k1M6aEAEFcGzkJiNy6J84y7uzo9M6NyMHAwCQYDV\
  R0TBAIwADAfBgNVHSMEGDAWgBRm3WjLa38lbEYCuiCPct0ZaSED2DAOBgNVHQ8BAf\
  8EBAMCBsAwEwYDVR0lBAwwCgYIKwYBBQUHAwIwHQYDVR0RAQH/BBMwEYEPYmRjQGV\
  4YW1wbGUuY29tMAoGCCqGSM49BAMCA0gAMEUCIBHda/r1vaL6G3VliL4/Di6YK0Q6\
  bMjeSkC3dFCOOB8TAiEAx/kHSB4urmiZ0NX5r5XarmPk0wmuydBVoU4hBVZ1yhk=:

{"hello": "world"}
~~~

Without a signature, the internal service would need to trust that the incoming connection has the right information. By signing the `Client-Cert` header and other portions of the internal request, the internal service can be assured that the correct party, the trusted proxy, has processed the request and presented it to the correct service. The proxy's signature input consists of the following:

~~~
NOTE: '\' line wrapping per RFC 8792

"@path": /foo
"@query": ?param=Value&Pet=dog
"@method": POST
"@authority": service.internal.example
"client-cert": :MIIBqDCCAU6gAwIBAgIBBzAKBggqhkjOPQQDAjA6MRswGQYDVQQ\
  KDBJMZXQncyBBdXRoZW50aWNhdGUxGzAZBgNVBAMMEkxBIEludGVybWVkaWF0ZSBD\
  QTAeFw0yMDAxMTQyMjU1MzNaFw0yMTAxMjMyMjU1MzNaMA0xCzAJBgNVBAMMAkJDM\
  FkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE8YnXXfaUgmnMtOXU/IncWalRhebrXm\
  ckC8vdgJ1p5Be5F/3YC8OthxM4+k1M6aEAEFcGzkJiNy6J84y7uzo9M6NyMHAwCQY\
  DVR0TBAIwADAfBgNVHSMEGDAWgBRm3WjLa38lbEYCuiCPct0ZaSED2DAOBgNVHQ8B\
  Af8EBAMCBsAwEwYDVR0lBAwwCgYIKwYBBQUHAwIwHQYDVR0RAQH/BBMwEYEPYmRjQ\
  GV4YW1wbGUuY29tMAoGCCqGSM49BAMCA0gAMEUCIBHda/r1vaL6G3VliL4/Di6YK0\
  Q6bMjeSkC3dFCOOB8TAiEAx/kHSB4urmiZ0NX5r5XarmPk0wmuydBVoU4hBVZ1yhk=:
"@signature-params": ("@path" "@query" "@method" "@authority" \
  "client-cert");created=1618884473;keyid="test-key-ecc-p256"
~~~

This results in the following signature:

~~~
NOTE: '\' line wrapping per RFC 8792

xVMHVpawaAC/0SbHrKRs9i8I3eOs5RtTMGCWXm/9nvZzoHsIg6Mce9315T6xoklyy0y\
zhD9ah4JHRwMLOgmizw==
~~~

Which results in the following signed request sent from the proxy to the internal service with the proxy's signature under the label `ttrp`:

~~~
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: service.internal.example
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Length: 18
Client-Cert: :MIIBqDCCAU6gAwIBAgIBBzAKBggqhkjOPQQDAjA6MRswGQYDVQQKD\
  BJMZXQncyBBdXRoZW50aWNhdGUxGzAZBgNVBAMMEkxBIEludGVybWVkaWF0ZSBDQT\
  AeFw0yMDAxMTQyMjU1MzNaFw0yMTAxMjMyMjU1MzNaMA0xCzAJBgNVBAMMAkJDMFk\
  wEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE8YnXXfaUgmnMtOXU/IncWalRhebrXmck\
  C8vdgJ1p5Be5F/3YC8OthxM4+k1M6aEAEFcGzkJiNy6J84y7uzo9M6NyMHAwCQYDV\
  R0TBAIwADAfBgNVHSMEGDAWgBRm3WjLa38lbEYCuiCPct0ZaSED2DAOBgNVHQ8BAf\
  8EBAMCBsAwEwYDVR0lBAwwCgYIKwYBBQUHAwIwHQYDVR0RAQH/BBMwEYEPYmRjQGV\
  4YW1wbGUuY29tMAoGCCqGSM49BAMCA0gAMEUCIBHda/r1vaL6G3VliL4/Di6YK0Q6\
  bMjeSkC3dFCOOB8TAiEAx/kHSB4urmiZ0NX5r5XarmPk0wmuydBVoU4hBVZ1yhk=:
Signature-Input: ttrp=("@path" "@query" "@method" "@authority" \
  "client-cert");created=1618884473;keyid="test-key-ecc-p256"
Signature: ttrp=:xVMHVpawaAC/0SbHrKRs9i8I3eOs5RtTMGCWXm/9nvZzoHsIg6\
  Mce9315T6xoklyy0yzhD9ah4JHRwMLOgmizw==:

{"hello": "world"}
~~~

The internal service can validate the proxy's signature and therefore be able to trust that the client's certificate has been appropriately processed.

# Acknowledgements {#acknowledgements}
{:numbered="false"}

This specification was initially based on the draft-cavage-http-signatures internet draft.  The editors would like to thank the authors of that draft, Mark Cavage and Manu Sporny, for their work on that draft and their continuing contributions. The specification also includes contributions from the draft-oauth-signed-http-request internet draft and other similar efforts.

The editors would also like to thank the following individuals for feedback, insight, and implementation of this draft and its predecessors (in alphabetical order):
Mark Adamcin,
Mark Allen,
Paul Annesley,
{{{Karl Böhlmark}}},
{{{Stéphane Bortzmeyer}}},
Sarven Capadisli,
Liam Dennehy,
Stephen Farrell,
Phillip Hallam-Baker,
Eric Holmes,
Andrey Kislyuk,
Adam Knight,
Dave Lehn,
Dave Longley,
Ilari Liusvaara,
James H. Manger,
Kathleen Moriarty,
Mark Nottingham,
Yoav Nir,
Adrian Palmer,
Lucas Pardue,
Roberto Polli,
Julian Reschke,
Michael Richardson,
Wojciech Rygielski,
Rich Salz,
Adam Scarr,
Cory J. Slep,
Dirk Stein,
Henry Story,
Lukasz Szewc,
Chris Webber, and
Jeffrey Yasskin.

# Document History
{:numbered="false"}

*RFC EDITOR: please remove this section before publication*

- draft-ietf-httpbis-message-signatures

  - -09
     * Explained key formats better.
     * Removed "host" and "date" from most examples.

  - -08
     * Editorial fixes.
     * Changed "specialty component" to "derived component".
     * Expanded signature input generation and ABNF rules.
     * Added Ed25519 algorithm.
     * Clarified encoding of ECDSA signature.
     * Clarified use of non-deterministic algorithms.

  - -07
     * Added security and privacy considerations.
     * Added pointers to algorithm values from definition sections.
     * Expanded IANA registry sections.
     * Clarified that the signing and verification algorithms take application requirements as inputs.
     * Defined "signature targets" of request, response, and related-response for specialty components.

  - -06
     * Updated language for message components, including identifiers and values.
     * Clarified that Signature-Input and Signature are fields which can be used as headers or trailers.
     * Add "Accept-Signature" field and semantics for signature negotiation.
     * Define new specialty content identifiers, re-defined request-target identifier.
     * Added request-response binding.

  - -05
     * Remove list prefixes.
     * Clarify signature algorithm parameters.
     * Update and fix examples.
     * Add examples for ECC and HMAC.

  - -04
     * Moved signature component definitions up to intro.
     * Created formal function definitions for algorithms to fulfill.
     * Updated all examples.
     * Added nonce parameter field.

  - -03
     * Clarified signing and verification processes.
     * Updated algorithm and key selection method.
     * Clearly defined core algorithm set.
     * Defined JOSE signature mapping process.
     * Removed legacy signature methods.
     * Define signature parameters separately from "signature" object model.
     * Define serialization values for signature-input header based on signature input.

  - -02
     * Removed editorial comments on document sources.
     * Removed in-document issues list in favor of tracked issues.
     * Replaced unstructured `Signature` header with `Signature-Input` and `Signature` Dictionary Structured Header Fields.
     * Defined content identifiers for individual Dictionary members, e.g., `"x-dictionary-field";key=member-name`.
     * Defined content identifiers for first N members of a List, e.g., `"x-list-field":prefix=4`.
     * Fixed up examples.
     * Updated introduction now that it's adopted.
     * Defined specialty content identifiers and a means to extend them.
     * Required signature parameters to be included in signature.
     * Added guidance on backwards compatibility, detection, and use of signature methods.

  - -01
     * Strengthened requirement for content identifiers for header fields to be lower-case (changed from SHOULD to MUST).
     * Added real example values for Creation Time and Expiration Time.
     * Minor editorial corrections and readability improvements.

  - -00
     * Initialized from draft-richanna-http-message-signatures-00, following adoption by the working group.

- draft-richanna-http-message-signatures
  - -00
     * Converted to xml2rfc v3 and reformatted to comply with RFC style guides.
     * Removed Signature auth-scheme definition and related content.
     * Removed conflicting normative requirements for use of algorithm parameter. Now MUST NOT be relied upon.
     * Removed Extensions appendix.
     * Rewrote abstract and introduction to explain context and need, and challenges inherent in signing HTTP messages.
     * Rewrote and heavily expanded algorithm definition, retaining normative requirements.
     * Added definitions for key terms, referenced RFC 7230 for HTTP terms.
     * Added examples for canonicalization and signature generation steps.
     * Rewrote Signature header definition, retaining normative requirements.
     * Added default values for algorithm and expires parameters.
     * Rewrote HTTP Signature Algorithms registry definition. Added change control policy and registry template. Removed suggested URI.
     * Added IANA HTTP Signature Parameter registry.
     * Added additional normative and informative references.
     * Added Topics for Working Group Discussion section, to be removed prior to publication as an RFC.
