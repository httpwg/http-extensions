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
    role: editor

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
    RFC6234:
    RFC7517:
    RFC7518:
    RFC8017:
    RFC8032:
    STRUCTURED-FIELDS: RFC8941
    FIPS186-4:
        target: https://csrc.nist.gov/publications/detail/fips/186/4/final
        title: Digital Signature Standard (DSS)
        date: 2013
    POSIX.1:
        target: https://pubs.opengroup.org/onlinepubs/9699919799/
        title: The Open Group Base Specifications Issue 7, 2018 edition
        date: 2018
    HTTP: RFC9110
    HTTP1: RFC9112
    URI: RFC3986
    HTMLURL:
        target: https://url.spec.whatwg.org/
        title: URL (Living Standard)
        date: 2021
    ABNF: RFC5234
informative:
    RFC7239:
    RFC8792:
    BCP195:
    CLIENT-CERT: I-D.ietf-httpbis-client-cert-field
    DIGEST: I-D.ietf-httpbis-digest-headers
    COOKIE: RFC6265

entity:
  SELF: "RFC nnnn"

--- abstract

This document describes a mechanism for creating, encoding, and verifying digital signatures or message authentication codes over components of an HTTP message. This mechanism supports use cases where the full HTTP message may not be known to the signer, and where the message may be transformed (e.g., by intermediaries) before reaching the verifier.
This document also describes a means for requesting that a signature be applied to a subsequent HTTP message in an ongoing HTTP exchange.

--- middle

# Introduction {#intro}

Message integrity and authenticity are security properties that are critical to the secure operation of many HTTP applications.
Application developers typically rely on the transport layer to provide these properties, by operating their application over {{?TLS=RFC8446}}. However, TLS only guarantees these properties over a single TLS connection, and the path between client and application may be composed of multiple independent TLS connections (for example, if the application is hosted behind a TLS-terminating gateway or if the client is behind a TLS Inspection appliance). In such cases, TLS cannot guarantee end-to-end message integrity or authenticity between the client and application. Additionally, some operating environments present obstacles that make it impractical to use TLS, or to use features necessary to provide message authenticity. Furthermore, some applications require the binding of an application-level key to the HTTP message, separate from any TLS certificates in use. Consequently, while TLS can meet message integrity and authenticity needs for many HTTP-based applications, it is not a universal solution.

This document defines a mechanism for providing end-to-end integrity and authenticity for components of an HTTP message. The mechanism allows applications to create digital signatures or message authentication codes (MACs) over only the components of the message that are meaningful and appropriate for the application. Strict canonicalization rules ensure that the verifier can verify the signature even if the message has been transformed in any of the many ways permitted by HTTP.

The signing mechanism described in this document consists of three parts:

- A common nomenclature and canonicalization rule set for the different protocol elements and other components of HTTP messages, used to create the signature base.
- Algorithms for generating and verifying signatures over HTTP message components using this signature base through application of cryptographic primitives.
- A mechanism for attaching a signature and related metadata to an HTTP message, and for parsing attached signatures and metadata from HTTP messages. To facilitate this, this document defines the "Signature-Input" and "Signature" fields.

This document also provides a mechanism for negotiation the use of signatures in one or more subsequent messages via the "Accept-Signature" field. This optional negotiation mechanism can be used along with opportunistic or application-driven message signatures by either party.

## Conventions and Terminology {#definitions}

{::boilerplate bcp14-tagged}

The terms "HTTP message", "HTTP request", "HTTP response",
"target URI", "gateway", "header field", "intermediary", "request target",
"trailer field", "sender", "method", and "recipient" are used as defined in {{HTTP}}.

For brevity, the term "signature" on its own is used in this document to refer to both digital signatures (which use asymmetric cryptography) and keyed MACs (which use symmetric cryptography). Similarly, the verb "sign" refers to the generation of either a digital signature or keyed MAC over a given signature base. The qualified term "digital signature" refers specifically to the output of an asymmetric cryptographic signing operation.

This document uses the following terminology from {{Section 3 of STRUCTURED-FIELDS}}
to specify data types: List, Inner List, Dictionary, Item, String, Integer, Byte Sequence, and Boolean.

This document defines several string constructions using {{ABNF}} and uses the following ABNF rules: `VCHAR`, `SP`, `DQUOTE`, `LF`. This document uses the following ABNF rules from {{STRUCTURED-FIELDS}}: `sf-string`, `inner-list`, `parameters`. This document uses the following ABNF rules from {{HTTP}}: `field-content`.

In addition to those listed above, this document uses the following terms:

{: vspace="0"}
HTTP Message Signature:
: A digital signature or keyed MAC that covers one or more portions of an HTTP message. Note that a given HTTP Message can contain multiple HTTP Message Signatures.

Signer:
: The entity that is generating or has generated an HTTP Message Signature. Note that multiple entities can act as signers and apply separate HTTP Message Signatures to a given HTTP Message.

Verifier:
: An entity that is verifying or has verified an HTTP Message Signature against an HTTP Message. Note that an HTTP Message Signature may be verified multiple times, potentially by different entities.

HTTP Message Component:
: A portion of an HTTP message that is capable of being covered by an HTTP Message Signature.

Derived Component:
: An HTTP Message Component derived from the HTTP message through the use of a specified algorithm or process. See {{derived-components}}.

HTTP Message Component Name:
: A string that identifies an HTTP Message Component's source, such as a field name or derived component name.

HTTP Message Component Identifier:
: The combination of an HTTP Message Component Name and any parameters that uniquely identifies a specific HTTP Message Component in respect to a particular HTTP Message Signature and the HTTP Message it applies to.

HTTP Message Component Value:
: The value associated with a given component identifier within the context of a particular HTTP Message. Component values are derived from the HTTP Message and are usually subject to a canonicalization process.

Covered Components:
: An ordered set of HTTP message component identifiers for fields ({{http-fields}}) and derived components ({{derived-components}}) that indicates the set of message components covered by the signature, never including the `@signature-params` identifier itself. The order of this set is preserved and communicated between the signer and verifier to facilitate reconstruction of the signature base.

Signature Base:
: The sequence of bytes generated by the signer and verifier using the covered components set and the HTTP Message. The signature base is processed by the cryptographic algorithm to produce or verify the HTTP Message Signature.

HTTP Message Signature Algorithm:
: A cryptographic algorithm that describes the signing and verification process for the signature, defined in terms of the `HTTP_SIGN` and `HTTP_VERIFY` primitives described in {{signature-methods}}.

Key Material:
: The key material required to create or verify the signature. The key material is often identified with an explicit key identifier, allowing the signer to indicate to the verifier which key was used.

Creation Time:
: A timestamp representing the point in time that the signature was generated, as asserted by the signer.

Expiration Time:
: A timestamp representing the point in time after which the signature should no longer be accepted by the verifier, as asserted by the signer.

Target Message:
: The HTTP message to which an HTTP Message Signature is applied.

Signature Context:
: The data source from which the HTTP Message Component Values are drawn. The context includes the target message and any additional information the signer or verifier might have, such as the full target URI of a request or the related request message for a response.

The term "Unix time" is defined by {{POSIX.1}}, [Section 4.16](http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html#tag_04_16).

This document contains non-normative examples of partial and complete HTTP messages. Some examples use a single trailing backslash `\` to indicate line wrapping for long values, as per {{RFC8792}}. The `\` character and leading spaces on wrapped lines are not part of the value.

## Requirements

HTTP permits and sometimes requires intermediaries to transform messages in a variety of ways. This can result in a recipient receiving a message that is not bitwise-equivalent to the message that was originally sent. In such a case, the recipient will be unable to verify integrity protections over the raw bytes of the sender's HTTP message, as verifying digital signatures or MACs requires both signer and verifier to have the exact same signature base. Since the exact raw bytes of the message cannot be relied upon as a reliable source for a signature base, the signer and verifier have to independently create the signature base from their respective versions of the message, via a mechanism that is resilient to safe changes that do not alter the meaning of the message.

For a variety of reasons, it is impractical to strictly define what constitutes a safe change versus an unsafe one. Applications use HTTP in a wide variety of ways and may disagree on whether a particular piece of information in a message (e.g., the message content, the method, or a particular header field) is relevant. Thus, a general purpose solution needs to provide signers with some degree of control over which message components are signed.

HTTP applications may be running in environments that do not provide complete access to or control over HTTP messages (such as a web browser's JavaScript environment), or may be using libraries that abstract away the details of the protocol (such as [the Java HTTPClient library](https://openjdk.java.net/groups/net/httpclient/intro.html)). These applications need to be able to generate and verify signatures despite incomplete knowledge of the HTTP message.

## HTTP Message Transformations {#transforms}

As mentioned earlier, HTTP explicitly permits and in some cases requires implementations to transform messages in a variety of ways. Implementations are required to tolerate many of these transformations. What follows is a non-normative and non-exhaustive list of transformations that could occur under HTTP, provided as context:

- Re-ordering of fields with different field names ({{Section 5.3 of HTTP}}).
- Combination of fields with the same field name ({{Section 5.2 of HTTP}}).
- Removal of fields listed in the Connection header field ({{Section 7.6.1 of HTTP}}).
- Addition of fields that indicate control options ({{Section 7.6.1 of HTTP}}).
- Addition or removal of a transfer coding ({{Section 7.7 of HTTP}}).
- Addition of fields such as `Via` ({{Section 7.6.3 of HTTP}}) and `Forwarded` ({{Section 4 of RFC7239}}).
- Conversion between different versions of the HTTP protocol (e.g., HTTP/1.x to HTTP/2, or vice-versa).
- Changes in casing (e.g., "Origin" to "origin") of any case-insensitive components such as field names, request URI scheme, or host.
- Addition or removal of leading or trailing whitespace to a field value.
- Addition or removal of `obs-folds` from field values.
- Changes to the request target and authority that when applied together do not
    result in a change to the message's target URI, as defined in {{Section 7.1 of HTTP}}.

We can identify these types of transformations as ones that should not prevent signature verification, even when performed on message components covered by the signature. Additionally, all changes to components not covered by the signature should not prevent signature verification.

Some examples of these kinds of transformations, and the effect they have on the message signature, are found in {{example-transform}}.

## Application of HTTP Message Signatures {#application}

HTTP Message Signatures are designed to be a general-purpose security mechanism applicable in a wide variety of circumstances and applications. In order to properly and safely apply HTTP Message Signatures, an application or profile of this specification MUST specify all of the following items:

- The set of [component identifiers](#covered-components) and [signature parameters](#signature-params) that are expected and required to be included in the covered components list. For example, an authorization protocol could mandate that the Authorization field be covered to protect the authorization credentials and mandate the signature parameters contain a `created` parameter, while an API expecting semantically relevant HTTP message content could require the Content-Digest field defined in {{DIGEST}} to be present and covered as well as mandate a value for `tag` that is specific to the API being protected.
- A means of retrieving the key material used to verify the signature. An application will usually use the `keyid` parameter of the signature parameters ({{signature-params}}) and define rules for resolving a key from there, though the appropriate key could be known from other means such as pre-registration of a signer's key.
- A means of determining the signature algorithm used to verify the signature is appropriate for the key material. For example, the process could use the `alg` parameter of the signature parameters ({{signature-params}}) to state the algorithm explicitly, derive the algorithm from the key material, or use some pre-configured algorithm agreed upon by the signer and verifier.
- A means of determining that a given key and algorithm presented in the request are appropriate for the request being made. For example, a server expecting only ECDSA signatures should know to reject any RSA signatures, or a server expecting asymmetric cryptography should know to reject any symmetric cryptography.
- A means of determining the context for derivation of message components from an HTTP message and its application context. While this is normally the target HTTP message itself, the context could include additional information known to the application, such as an external host name.

When choosing these parameters, an application of HTTP message signatures has to ensure that the verifier will have access to all required information needed to re-create the signature base. For example, a server behind a reverse proxy would need to know the original request URI to make use of the derived component `@target-uri`, even though the apparent target URI would be changed by the reverse proxy (see also {{security-message-component-context}}). Additionally, an application using signatures in responses would need to ensure that clients receiving signed responses have access to all the signed portions of the message, including any portions of the request that were signed by the server using the related-response parameter.

The details of this kind of profiling are the purview of the application and outside the scope of this specification, however some additional considerations are discussed in {{security}}. In particular, when choosing the required set of component identifiers, care has to be taken to make sure that the coverage is sufficient for the application, as discussed in {{security-coverage}} and  {{security-message-content}}.

# HTTP Message Components {#covered-components}

In order to allow signers and verifiers to establish which components are covered by a signature, this document defines component identifiers for components covered by an HTTP Message Signature, a set of rules for deriving and canonicalizing the values associated with these component identifiers from the HTTP Message, and the means for combining these canonicalized values into a signature base.

The signature context for deriving these values MUST be accessible to both the signer and the verifier of the message. The context MUST be the same across all components in a given signature. For example, it would be an error to use a the raw query string for the `@query` derived component but combined query and form parameters for the `@query-param` derived component. For more considerations of the message component context, see {{security-message-component-context}}.

A component identifier is composed of a component name and any parameters associated with that name. Each component name is either an HTTP field name ({{http-fields}}) or a registered derived component name ({{derived-components}}). The possible parameters for a component identifier are dependent on the component identifier, and a registry cataloging all possible parameters is defined in {{param-registry}}.

Within a single list of covered components, each component identifier MUST occur only once. One component identifier is distinct from another if either the component name or its parameters differ. Multiple component identifiers having the same component name MAY be included if they have parameters that make them distinct. The order of parameters MUST be preserved when processing a component identifier (such as when parsing during verification), but the order of parameters is not significant when comparing two component identifiers for equality. That is to say, `"foo";bar;baz` cannot be in the same message as `"foo";baz;bar`, since these two component identifiers are equivalent, but a system processing one form is not allowed to transform it into the other form.

The component value associated with a component identifier is defined by the identifier itself. Component values MUST NOT contain newline (`\n`) characters. Some HTTP message components can undergo transformations that change the bitwise value without altering the meaning of the component's value (for example, when combining field values). Message component values must therefore be canonicalized before they are signed, to ensure that a signature can be verified despite such intermediary transformations. This document defines rules for each component identifier that transform the identifier's associated component value into such a canonical form.

The following sections define component identifier names, their parameters, their associated values, and the canonicalization rules for their values. The method for combining message components into the signature base is defined in {{create-sig-input}}.

## HTTP Fields {#http-fields}

The component name for an HTTP field is the lowercased form of its field name as defined in {{Section 5.1 of HTTP}}. While HTTP field names are case-insensitive, implementations MUST use lowercased field names (e.g., `content-type`, `date`, `etag`) when using them as component names.

The component value for an HTTP field is the field value for the named field as defined in {{Section 5.5 of HTTP}}. The field value MUST be taken from the named header field of the target message unless this behavior is overridden by additional parameters and rules, such as the `req` and `tr` flags, below.

Unless overridden by additional parameters and rules, HTTP field values MUST be combined into a single value as defined in {{Section 5.2 of HTTP}} to create the component value. Specifically, HTTP fields sent as multiple fields MUST be combined using a single comma (",") and a single space (" ") between each item. Note that intermediaries are allowed to combine values of HTTP fields with any amount of whitespace between the commas, and if this behavior is not accounted for by the verifier, the signature can fail since the signer and verifier will be see a different component value in their respective signature bases. For robustness, it is RECOMMENDED that signed messages include only a single instance of any field covered under the signature, particularly with the value for any list-based fields serialized using the algorithm below. This approach increases the chances of the field value remaining untouched through intermediaries. Where that approach is not possible and multiple instances of a field need to be sent separately, it is RECOMMENDED that signers and verifiers process any list-based fields by parsing out individual field values and combining them based on the strict algorithm below, to counter possible intermediary behavior. When the field in question is a structured field of type List or Dictionary, this effect can be accomplished more directly by using the strict structured field serialization of the field value, as described in {{http-field-structured}}.

Note that some HTTP fields, such as Set-Cookie {{COOKIE}}, do not follow a syntax that allows for combination of field values in this manner (such that the combined output is unambiguous from multiple inputs). Even though the component value is never parsed by the message signature process and used only as part of the signature base in {{create-sig-input}}, caution needs to be taken when including such fields in signatures since the combined value could be ambiguous. The `bs` parameter defined in {{http-field-byte-sequence}} provides a method for wrapping such problematic fields. See {{security-non-list}} for more discussion of this issue.

If the correctly combined value is not directly available for a given field by an implementation, the following algorithm will produce canonicalized results for list-based fields:

1. Create an ordered list of the field values of each instance of the field in the message, in the order that they occur (or will occur) in the message. If necessary, separate individual values found in a field instance.
2. Strip leading and trailing whitespace from each item in the list. Note that since HTTP field values are not allowed to contain leading and trailing whitespace, this will be a no-op in a compliant implementation.
3. Remove any obsolete line-folding within the line and replace it with a single space (" "), as discussed in {{Section 5.2 of HTTP1}}. Note that this behavior is specific to {{HTTP1}} and does not apply to other versions of the HTTP specification which do not allow internal line folding.
4. Concatenate the list of values together with a single comma (",") and a single space (" ") between each item.

The resulting string is the component value for the field.

Note that some HTTP fields have values with multiple valid serializations that have equivalent semantics, such as allow case-insensitive values that intermediaries could change. Applications signing and processing such fields MUST consider how to handle the values of such fields to ensure that the signer and verifier can derive the same value, as discussed in {{security-field-values}}.

Following are non-normative examples of component values for header fields, given the following example HTTP message fragment:

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

The following example shows the component values for these example header fields, presented using the signature base format defined in in {{create-sig-input}}:

~~~
"host": www.example.com
"date": Tue, 20 Apr 2021 02:07:56 GMT
"x-ows-header": Leading and trailing whitespace.
"x-obs-fold-header": Obsolete line folding.
"cache-control": max-age=60, must-revalidate
"example-dict": a=1,    b=2;x=1;y=2,   c=(a   b   c)
~~~

Since empty HTTP fields are allowed, they can also be signed when present in a message. The canonicalized value is the empty string. This means that the following empty header, with <SP> indicating a single space character:

~~~ http-message
X-Empty-Header:<SP>
~~~

Is serialized by the [signature base generation algorithm](#create-sig-input) with an empty string value following the colon and space added after the content identifier.

~~~
"x-empty-header":<SP>
~~~

Any HTTP field component identifiers MAY have the following parameters in specific circumstances, each described in detail in their own sections:

`sf`
: A boolean flag indicating that the component value is serialized using strict encoding
of the structured field value ({{http-field-structured}}).

`key`
: A string parameter used to select a single member value from a Dictionary structured field ({{http-field-dictionary}}).

`bs`
: A boolean flag indicating that individual field values are encoded using Byte Sequence data structures before being combined into the component value ({{http-field-byte-sequence}}).

`req`
: A boolean flag for signed responses indicating that the component value is derived from the request that triggered this response message and not from the response message directly. Note that this parameter can also be applied to any derived component identifiers that target the request ({{content-request-response}}).

`tr`
: A boolean flag indicating that the field value is taken from the trailers of the message as defined in {{Section 6.5 of HTTP}}. If this flag is absent, the field value is taken from the headers of the message as defined in {{Section 6.3 of HTTP}} ({{http-trailer}}).

Multiple parameters MAY be specified together, though some combinations are redundant or incompatible. For example, the `sf` parameter's functionality is already covered when the `key` parameter is used on a dictionary item, since `key` requires strict serialization of the value. The `bs` parameter, which requires the raw field values from the message, is not compatible with use of the `sf` or `key` parameters, which require the parsed data structures of the field values after combination.

Additional parameters can be defined in the HTTP Signature Component Parameters registry established in {{component-param-registry}}.

### Strict Serialization of HTTP Structured Fields {#http-field-structured}

If the value of an HTTP field is known by the application to be a structured field ({{STRUCTURED-FIELDS}}), and the expected type of the structured field is known, the signer MAY include the `sf` parameter in the component identifier.
If this parameter is included with a component identifier, the HTTP field value MUST be serialized using the rules specified in {{Section 4 of STRUCTURED-FIELDS}} applicable to the type of the HTTP field. Note that this process
will replace any optional internal whitespace with a single space character, among other potential transformations of the value.

If multiple field values occur within a message, these values MUST be combined into a single List or Dictionary structure before serialization.

For example, the following dictionary field is a valid serialization:

~~~ http-message
Example-Dict:  a=1,    b=2;x=1;y=2,   c=(a   b   c)
~~~

If included in the signature base without parameters, its value would be:

~~~
"example-dict": a=1,    b=2;x=1;y=2,   c=(a   b   c)
~~~

However, if the `sf` parameter is added, the value is re-serialized as follows:

~~~
"example-dict";sf: a=1, b=2;x=1;y=2, c=(a b c)
~~~

The resulting string is used as the component value in {{http-fields}}.

### Dictionary Structured Field Members {#http-field-dictionary}

If a given field is known by the application to be a Dictionary structured field, an individual member in the value of that Dictionary is identified by using the parameter `key` and the Dictionary member key as a String value.

If multiple field values occur within a message, these values MUST be combined into a single Dictionary structure before serialization.

An individual member value of a Dictionary Structured Field is canonicalized by applying the serialization algorithm described in {{Section 4.1.2 of STRUCTURED-FIELDS}} on the `member_value` and its parameters, not including the dictionary key itself. Specifically, the value is serialized as an Item or Inner List (the two possible values of a Dictionary member).

Each parameterized key for a given field MUST NOT appear more than once in the signature base. Parameterized keys MAY appear in any order in the signature base, regardless of the order they occur in the source Dictionary.

If a Dictionary key is named as a covered component but it does not occur in the Dictionary, this MUST cause an error in the signature base generation.

Following are non-normative examples of canonicalized values for Dictionary structured field members given the following example header field, whose value is known by the application to be a Dictionary:

~~~ http-message
Example-Dict:  a=1, b=2;x=1;y=2, c=(a   b    c), d
~~~

The following example shows canonicalized values for different component identifiers of this field, presented using the signature base format discussed in {{create-sig-input}}:

~~~
"example-dict";key="a": 1
"example-dict";key="d": ?1
"example-dict";key="b": 2;x=1;y=2
"example-dict";key="c": (a b c)
~~~

Note that the value for `key="c"` has been re-serialized according to the strict `member_value` algorithm, and the value for `key="d"` has been serialized as a Boolean value.

### Binary-wrapped HTTP Fields {#http-field-byte-sequence}

If the value of the the HTTP field in question is known by the application to cause problems with serialization, particularly with the combination of multiple values into a single line as discussed in {{security-non-list}}, the signer SHOULD include the `bs` parameter in a component identifier to indicate the values of the fields need to be wrapped as binary structures before being combined.

If this parameter is included with a component identifier, the component value MUST be calculated using the following algorithm:

0. Let the input be the ordered set of values for a field, in the order they appear in the message.
1. Create an empty List for accumulating processed field values.
2. For each field value in the set:
    0. Strip leading and trailing whitespace from the field value. Note that since HTTP field values are not allowed to contain leading and trailing whitespace, this will be a no-op in a compliant implementation.
    1. Remove any obsolete line-folding within the line and replace it with a single space (" "), as discussed in {{Section 5.2 of HTTP1}}. Note that this behavior is specific to {{HTTP1}} and does not apply to other versions of the HTTP specification.
    2. Encode the bytes of the resulting field value's ASCII representation as a Byte Sequence.
    3. Add the Byte Sequence to the List accumulator.
3. The intermediate result is a List of Byte Sequence values.
4. Follow the strict serialization of a List as described in {{Section 4.1.1 of STRUCTURED-FIELDS}} and return this output.

For example, the following field with internal commas prevents the distinct field values from being safely combined:

~~~ http-message
Example-Header: value, with, lots
Example-Header: of, commas
~~~

In our example, the same field can be sent with a semantically different single value:

~~~ http-message
Example-Header: value, with, lots, of, commas
~~~

Both of these versions are treated differently by the application. however, if included in the signature base without parameters, the component value would be the same in both cases:

~~~
"example-header": value, with, lots, of, commas
~~~

However, if the `bs` parameter is added, the two separate instances are encoded and serialized as follows:

~~~
"example-header";bs: :dmFsdWUsIHdpdGgsIGxvdHM=:, :b2YsIGNvbW1hcw==:
~~~

For the single-instance field above, the encoding with the `bs` parameter is:

~~~
"example-header";bs: :dmFsdWUsIHdpdGgsIGxvdHMsIG9mLCBjb21tYXM=:
~~~

This component value is distinct from the multiple-instance field above, preventing a collision which could potentially be exploited.

### Trailer Fields {#http-trailer}

If the signer wants to include a trailer field in the signature, the signer MUST include the `tr` boolean parameter to indicate the value MUST be taken from the trailer fields and not from the header fields.

For example, given the following message:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: text/plain
Transfer-Encoding: chunked
Trailer: Expires

4
HTTP
7
Message
a
Signatures
0
Expires: Wed, 9 Nov 2022 07:28:00 GMT
~~~

The signer decides to add both the Trailer header field as well as the Expires trailer to the signature base, along with the status code derived component:

~~~
"@status": 200
"trailer": Expires
"expires";tr: Wed, 9 Nov 2022 07:28:00 GMT
~~~

If a field is available as both a header and trailer in a message, both values MAY be signed, but the values MUST be signed separately. The values of header fields and trailer fields of the same name MUST NOT be combined for purposes of the signature.

Since trailer fields could be merged into the header fields or dropped entirely by intermediaries as per {{Section 6.5.1 of HTTP}}, it is NOT RECOMMENDED to include trailers in the signature unless the signer knows that the verifier will have access to the values of the trailers as sent.

## Derived Components {#derived-components}

In addition to HTTP fields, there are a number of different components that can be derived from the control data, signature context, or other aspects of the HTTP message being signed. Such derived components can be included in the signature base by defining a component name, possible parameters, message target, and the derivation method for its component value.

Derived component names MUST start with the "at" `@` character. This differentiates derived component names from HTTP field names, which cannot contain the `@` character as per {{Section 5.1 of HTTP}}. Processors of HTTP Message Signatures MUST treat derived component names separately from field names, as discussed in {{security-lazy-header-parser}}.

This specification defines the following derived components:

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

@query-param
: A parsed query parameter of the target URI for a request. ({{content-request-query-param}})

@status
: The status code for a response. ({{content-status-code}})

Additional derived component names are defined in the HTTP Signatures Derived Component Name Registry. ({{content-registry}})

Derived component values are taken from the context of the target message for the signature. This context includes information about the message itself, such as its control data, as well as any additional state and context held by the signer or verifier. In particular, when signing a response, the signer can include any derived components from the originating request by using the [request-response signature binding parameter](#content-request-response).

request:
: Values derived from and results applied to an HTTP request message as described in {{Section 3.4 of HTTP}}. If the target message of the signature is a response, using the `req` parameter allows a request-targeted derived component to be included in the signature (see {{content-request-response}}).

response:
: Values derived from and results applied to an HTTP response message as described in {{Section 3.4 of HTTP}}.

A derived component definition MUST define all target message types to which it can be applied.

Derived component values MUST be limited to printable characters and spaces and MUST NOT contain any newline characters. Derived component values MUST NOT start or end with whitespace characters.

### Method {#content-request-method}

The `@method` derived component refers to the HTTP method of a request message. The component value is canonicalized by taking the value of the method as a string. Note that the method name is case-sensitive as per {{HTTP, Section 9.1}}, and conventionally standardized method names are uppercase US-ASCII.

For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@method` component value:

~~~
POST
~~~

And the following signature base line:

~~~
"@method": POST
~~~

### Target URI {#content-target-uri}

The `@target-uri` derived component refers to the target URI of a request message. The component value is the full absolute target URI of the request, potentially assembled from all available parts including the authority and request target as described in {{HTTP, Section 7.1}}.

For example, the following message sent over HTTPS:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@target-uri` component value:

~~~
https://www.example.com/path?param=value
~~~

And the following signature base line:

~~~
"@target-uri": https://www.example.com/path?param=value
~~~

### Authority {#content-request-authority}

The `@authority` derived component refers to the authority component of the target URI of the HTTP request message, as defined in {{HTTP, Section 7.2}}. In HTTP/1.1, this is usually conveyed using the Host header, while in HTTP/2 and HTTP/3 it is conveyed using the :authority pseudo-header. The value is the fully-qualified authority component of the request, comprised of the host and, optionally, port of the request target, as a string.
The component value MUST be normalized according to the rules in {{HTTP, Section 4.2.3}}. Namely, the host name is normalized to lowercase and the default port is omitted.

For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@authority` component value:

~~~
www.example.com
~~~

And the following signature base line:

~~~
"@authority": www.example.com
~~~

The `@authority` derived component SHOULD be used instead of signing the Host header directly, see {{security-not-fields}}.

### Scheme {#content-request-scheme}

The `@scheme` derived component refers to the scheme of the target URL of the HTTP request message. The component value is the scheme as a lowercase string as defined in {{HTTP, Section 4.2}}.
While the scheme itself is case-insensitive, it MUST be normalized to lowercase for
inclusion in the signature base.

For example, the following request message requested over plain HTTP:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@scheme` component value:

~~~
http
~~~

And the following signature base line:

~~~
"@scheme": http
~~~

### Request Target {#content-request-target}

The `@request-target` derived component refers to the full request target of the HTTP request message,
as defined in {{HTTP, Section 7.1}}. The component value of the request target can take different forms,
depending on the type of request, as described below.

For HTTP/1.1, the component value is equivalent to the request target
portion of the request line. However, this value is more difficult to reliably construct in
other versions of HTTP. Therefore, it is NOT RECOMMENDED that this component be used
when versions of HTTP other than 1.1 might be in use.

The origin form value is combination of the absolute path and query components of the request URL. For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@request-target` component value:

~~~
/path?param=value
~~~

And the following signature base line:

~~~
"@request-target": /path?param=value
~~~

The following request to an HTTP proxy with the absolute-form value, containing the fully qualified target URI:

~~~ http-message
GET https://www.example.com/path?param=value HTTP/1.1
~~~

Would result in the following `@request-target` component value:

~~~
https://www.example.com/path?param=value
~~~

And the following signature base line:

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
www.example.com:80
~~~

And the following signature base line:

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
*
~~~

And the following signature base line:

~~~
"@request-target": *
~~~

### Path {#content-request-path}

The `@path` derived component refers to the target path of the HTTP request message. The component value is the absolute path of the request target defined by {{URI}}, with no query component and no trailing `?` character. The value is normalized according to the rules in {{HTTP, Section 4.2.3}}. Namely, an empty path string is normalized as a single slash `/` character. Path components are represented by their values before decoding any percent-encoded octets, as described in the simple string comparison rules in {{Section 6.2.1 of URI}}.

For example, the following request message:

~~~ http-message
POST /path?param=value HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@path` component value:

~~~
/path
~~~

And the following signature base line:

~~~
"@path": /path
~~~

### Query {#content-request-query}

The `@query` derived component refers to the query component of the HTTP request message. The component value is the entire normalized query string defined by {{URI}}, including the leading `?` character. The value is read using the simple string comparison rules in {{Section 6.2.1 of URI}}. Namely, percent-encoded octets are not decoded.

For example, the following request message:

~~~ http-message
POST /path?param=value&foo=bar&baz=bat%2Dman HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@query` component value:

~~~
?param=value&foo=bar&baz=bat%2Dman
~~~

And the following signature base line:

~~~
"@query": ?param=value&foo=bar&baz=bat%2Dman
~~~

The following request message:

~~~ http-message
POST /path?queryString HTTP/1.1
Host: www.example.com
~~~

Would result in the following `@query` component value:

~~~
?queryString
~~~

And the following signature base line:

~~~
"@query": ?queryString
~~~

If the query string is absent from the request message, the value is the leading `?` character alone:

~~~
?
~~~

Resulting in the following signature base line:

~~~
"@query": ?
~~~

### Query Parameters {#content-request-query-param}

If a request target URI uses HTML form parameters in the query string as defined in [HTMLURL, Section 5](#HTMLURL),
the `@query-param` derived component allows addressing of individual query parameters. The query parameters MUST be parsed according to [HTMLURL, Section 5.1](#HTMLURL), resulting in a list of (`nameString`, `valueString`) tuples.
The REQUIRED `name` parameter of each component identifier contains the `nameString` of a single query parameter as a String value.
Several different named query parameters MAY be included in the covered components.
Single named parameters MAY occur in any order in the covered components.

The component value of a single named parameter is the `valueString` of the named query parameter defined by [HTMLURL, Section 5.1](#HTMLURL), which is the value after percent-encoded octets are decoded.
Note that this value does not include any leading `?` characters, equals sign `=`, or separating `&` characters.
Named query parameters with an empty `valueString` are included with an empty string as the component value.

If a query parameter is named as a covered component but it does not occur in the query parameters, this MUST cause an error in the signature base generation.

For example for the following request:

~~~ http-message
POST /path?param=value&foo=bar&baz=batman&qux= HTTP/1.1
Host: www.example.com
~~~

Indicating the `baz`, `qux` and `param` named query parameters would result in the following `@query-param` component values:

*baz*: `batman`

*qux*: an empty string

*param*: `value`

And the following signature base lines:

~~~
NOTE: '\' line wrapping per RFC 8792

"@query-param";name="baz": batman
"@query-param";name="qux": \

"@query-param";name="param": value
~~~

If a parameter name occurs multiple times in a request, all parameter values of that name MUST be included
in separate signature base lines in the order in which the parameters occur in the target URI. Note that in some implementations, the order of parsed query parameters is not stable, and this situation could lead to unexpected results. If multiple parameters are common within an application, it is RECOMMENDED to sign the entire query string using the `@query` component identifier defined in {{content-request-query}}.

### Status Code {#content-status-code}

The `@status` derived component refers to the three-digit numeric HTTP status code of a response message as defined in {{HTTP, Section 15}}. The component value is the serialized three-digit integer of the HTTP status code, with no descriptive text.

For example, the following response message:

~~~ http-message
HTTP/1.1 200 OK
Date: Fri, 26 Mar 2010 00:05:00 GMT
~~~

Would result in the following `@status` component value:

~~~
200
~~~

And the following signature base line:

~~~
"@status": 200
~~~

The `@status` component identifier MUST NOT be used in a request message.

## Signature Parameters {#signature-params}

HTTP Message Signatures have metadata properties that provide information regarding the signature's generation and verification, consisting of the ordered set of covered components and the ordered set of parameters including a timestamp of signature creation, identifiers for verification key material, and other utilities. This metadata is represented by a special derived component for signature parameters, and it is treated slightly differently from other derived components. Specifically, the signature parameters message component is REQUIRED as the last line of the [signature base](#create-sig-input), and the component identifier MUST NOT be enumerated within the set of covered components for any signature, including itself.

The signature parameters component name is `@signature-params`.

The signature parameters component value is the serialization of the signature parameters for this signature, including the covered components ordered set with all associated parameters. These parameters include any of the following:

* `created`: Creation time as an Integer UNIX timestamp value. Sub-second precision is not supported. Inclusion of this parameter is RECOMMENDED.
* `expires`: Expiration time as an Integer UNIX timestamp value. Sub-second precision is not supported.
* `nonce`: A random unique value generated for this signature as a String value.
* `alg`: The HTTP message signature algorithm from the HTTP Message Signature Algorithm Registry, as a String value.
* `keyid`: The identifier for the key material as a String value.
* `tag`: An application-specific tag for the signature as a String value. This value is used by applications to help identify signatures relevant for specific applications or protocols.

Additional parameters can be defined in the [HTTP Signature Parameters Registry](#iana-param-contents). Note that there is no general ordering to the parameters, but once an ordering is chosen for a given set of parameters, it cannot be changed without altering the signature parameters value.

The signature parameters component value is serialized as a parameterized Inner List using the rules in {{Section 4 of STRUCTURED-FIELDS}} as follows:

1. Let the output be an empty string.
2. Determine an order for the component identifiers of the covered components, not including the `@signature-params` component identifier itself. Once this order is chosen, it cannot be changed. This order MUST be the same order as used in creating the signature base ({{create-sig-input}}).
3. Serialize the component identifiers of the covered components, including all parameters, as an ordered Inner List of String values according to {{Section 4.1.1.1 of STRUCTURED-FIELDS}} and append this to the output. Note that the component identifiers can include their own parameters, and these parameters are ordered sets. Once an order is chosen for a component's parameters, the order cannot be changed.
4. Determine an order for any signature parameters. Once this order is chosen, it cannot be changed.
5. Append the parameters to the Inner List in order according to {{Section 4.1.1.2 of STRUCTURED-FIELDS}},
    skipping parameters that are not available or not used for this message signature.
6. The output contains the signature parameters component value.

Note that the Inner List serialization from {{Section 4.1.1.1 of STRUCTURED-FIELDS}} is used for the covered component value instead of the List serialization from {{Section 4.1.1 of STRUCTURED-FIELDS}}
in order to facilitate parallelism with this value's inclusion in the Signature-Input field,
as discussed in {{signature-input-header}}.

This example shows the serialized component value for the parameters of an example message signature:

~~~
NOTE: '\' line wrapping per RFC 8792

("@target-uri" "@authority" "date" "cache-control")\
  ;keyid="test-key-rsa-pss";alg="rsa-pss-sha512";\
  created=1618884475;expires=1618884775
~~~

Note that an HTTP message could contain [multiple signatures](#signature-multiple), but only the signature parameters used for a single signature are included in a given signature parameters entry.

## Request-Response Signature Binding {#content-request-response}

When a request message results in a signed response message, the signer can include portions of the request message in the signature base by adding the `req` parameter to the component identifier.

`req`
: A boolean flag indicating that the component value is derived from the request that triggered this response message and not from the response message directly.

This parameter can be applied to both HTTP fields and derived components that target the request, with the same semantics. The component value for a message component using this parameter is calculated in the same manner as it is normally, but data is pulled from the request message instead of the target response message to which the signature is applied.

Note that the same component name MAY be included with and without the `req` parameter in a single signature base, indicating the same named component from both the request and response message.

The `req` parameter MAY be combined with other parameters as appropriate for the component identifier, such as the `key` parameter for a dictionary field.

For example, when serving a response for this signed request:

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

To cryptographically link the response to the request, the server signs the response with its own key and includes the method, authority, and the signature value `sig1` from the request in the covered components of the response. The signature base for this example is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@status": 503
"content-length": 62
"content-type": application/json
"signature";req;key="sig1": :LAH8BjcfcOcLojiuOBFWn0P5keD3xAOuJRGziC\
  LuD8r5MW9S0RoXXLzLSRfGY/3SF8kVIkHjE13SEFdTo4Af/fJ/Pu9wheqoLVdwXyY\
  /UkBIS1M8Brc8IODsn5DFIrG0IrburbLi0uCc+E2ZIIb6HbUJ+o+jP58JelMTe0QE\
  3IpWINTEzpxjqDf5/Df+InHCAkQCTuKsamjWXUpyOT1Wkxi7YPVNOjW4MfNuTZ9Hd\
  bD2Tr65+BXeTG9ZS/9SWuXAc+BZ8WyPz0QRz//ec3uWXd7bYYODSjRAxHqX+S1ag3\
  LZElYyUKaAIjZ8MGOt4gXEwCSLDv/zqxZeWLj/PDkn6w==:
"@authority";req: example.com
"@method";req: POST
"@signature-params": ("@status" "content-length" "content-type" \
  "signature";req;key="sig1" "@authority";req "@method";req)\
  ;created=1618884479;keyid="test-key-ecc-p256"
~~~

The signed response message is:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

HTTP/1.1 503 Service Unavailable
Date: Tue, 20 Apr 2021 02:07:56 GMT
Content-Type: application/json
Content-Length: 62
Signature-Input: reqres=("@status" "content-length" "content-type" \
  "signature";req;key="sig1" "@authority";req "@method";req)\
  ;created=1618884479;keyid="test-key-ecc-p256"
Signature: reqres=:mh17P4TbYYBmBwsXPT4nsyVzW4Rp9Fb8WcvnfqKCQLoMvzOB\
  LD/n32tL/GPW6XE5GAS5bdsg1khK6lBzV1Cx/Q==:

{"busy": true, "message": "Your call is very important to us"}
~~~

Since the request's signature value itself is not repeated in the response, the requester MUST keep the original signature value around long enough to validate the signature of the response that uses this component identifier.

Note that the ECDSA algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

The `req` parameter MUST NOT be used in a signature that targets a request message.

## Creating the Signature Base {#create-sig-input}

The signature base is a US-ASCII string containing the canonicalized HTTP message components covered by the signature. The input to the signature base creation algorithm is the ordered set of covered component identifiers and their associated values, along with any additional signature parameters discussed in {{signature-params}}.

Component identifiers are serialized using the production grammar defined by {{STRUCTURED-FIELDS, Section 4}}.
The component identifier has a component name, which is a String Item value serialized using the `sf-string` ABNF rule. The component identifier MAY also include defined parameters which are serialized using the `parameters` ABNF rule. The signature parameters line defined in {{signature-params}} follows this same pattern, but the component identifier is a String Item with a fixed value and no parameters, and the component value is always an Inner List with optional parameters.

Note that this means the serialization of the component name itself is encased in double quotes, with parameters following as a semicolon-separated list, such as `"cache-control"`, `"@authority"`, `"@signature-params"`, or `"example-dictionary";key="foo"`.

The output is the ordered set of bytes that form the signature base, which conforms to the following ABNF:

~~~ abnf
signature-base = *( signature-base-line LF ) signature-params-line
signature-base-line = component-identifier ":" SP
    ( derived-component-value / field-content ) ; no obs-fold
component-identifier = component-name parameters
component-name = sf-string
derived-component-value = *( VCHAR / SP )
signature-params-line = DQUOTE "@signature-params" DQUOTE
     ":" SP inner-list
~~~

To create the signature base, the signer or verifier concatenates together entries for each component identifier in the signature's covered components (including their parameters) using the following algorithm. All errors produced as described immediately MUST fail the algorithm with no signature output base output.

1. Let the output be an empty string.

2. For each message component item in the covered components set (in order):

    1. Append the component identifier for the covered component serialized according to the `component-identifier` ABNF rule. Note that this serialization places the component name in double quotes and appends any parameters outside of the quotes.

    2. Append a single colon `:`

    3. Append a single space " "

    4. Determine the component value for the component identifier.

        - If the component identifier has a parameter that is not understood, produce an error.

        - If the component identifier has several incompatible parameters, such as `bs` and `sf`, produce an error.

        - If the component identifier contains the `req` parameter and the target message is a request, produce an error.

        - If the component identifier contains the `req` parameter and the target message is a response, the context for the component value is the related request message of the target response message. Otherwise, the context for the component value is the target message.

        - If the component name starts with an "at" character (`@`), derive the component's value from the message according to the specific rules defined for the derived component, as in {{derived-components}}, including processing of any known valid parameters. If the derived component name is unknown or the value cannot be derived, produce an error.

        - If the component name does not start with an "at" character (`@`), canonicalize the HTTP field value as described in {{http-fields}}, including processing of any known valid parameters. If the field cannot be found in the message, or the value cannot be obtained in the context, produce an error.

    5. Append the covered component's canonicalized component value.

    6. Append a single newline `\n`

3. Append the signature parameters component ({{signature-params}}) according to the `signature-params-line` rule as follows:

    1. Append the component identifier for the signature parameters serialized according to the `component-identifier` rule, i.e. the exact value `"@signature-params"` (including double quotes)

    2. Append a single colon `:`

    3. Append a single space " "

    4. Append the signature parameters' canonicalized component value as defined in {{signature-params}}, i.e. an Inner List structured field value with parameters

4. Return the output string.

If covered components reference a component identifier that cannot be resolved to a component value in the message, the implementation MUST produce an error and not create a signature base. Such situations are included but not limited to:

 * The signer or verifier does not understand the derived component name.
 * The component name identifies a field that is not present in the message or whose value is malformed.
 * The component identifier includes a parameter that is unknown or does not apply to the component identifier to which it is attached.
 * The component identifier indicates that a structured field serialization is used (via the `sf` parameter), but the field in question is known to not be a structured field or the type of structured field is not known to the implementation.
 * The component identifier is a dictionary member identifier that references a field that is not present in the message, is not a Dictionary Structured Field, or whose value is malformed.
 * The component identifier is a dictionary member identifier or a named query parameter identifier that references a member that is not present in the component value, or whose value is malformed. E.g., the identifier is `"example-dict";key="c"` and the value of the Example-Dict header field is `a=1, b=2`, which does not have the `c` value.

In the following non-normative example, the HTTP message being signed is the following request:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /foo?param=Value&Pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Content-Digest: sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX+T\
  aPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
Content-Length: 18

{"hello": "world"}
~~~

The covered components consist of the `@method`, `@authority`, and `@path` derived components followed by the `Content-Digest`, `Content-Length`, and `Content-Type` HTTP header fields, in order. The signature parameters consist of a creation timestamp of `1618884473` and a key identifier of `test-key-rsa-pss`. Note that no explicit `alg` parameter is given here since the verifier is known by the application to use the RSA PSS algorithm based on the identified key. The signature base for this message with these parameters is:

~~~ http-message
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
{: title="Non-normative example Signature Base" artwork-name="example-sig-input" #example-sig-input}

Note that the example signature base here, or anywhere else within this specification, does not include the final newline that ends the displayed example.

# HTTP Message Signatures {#message-signatures}

An HTTP Message Signature is a signature over a string generated from a subset of the components of an HTTP message in addition to metadata about the signature itself. When successfully verified against an HTTP message, an HTTP Message Signature provides cryptographic proof that the message is semantically equivalent to the message for which the signature was generated, with respect to the subset of message components that was signed.

## Creating a Signature {#sign}

Creation of an HTTP message signature is a process that takes as its input the signature context (including the target message) and the requirements for the application. The output is a signature value and set of signature parameters that can be communicated to the verifier by adding them to the message.

In order to create a signature, a signer MUST follow the following algorithm:

1. The signer chooses an HTTP signature algorithm and key material for signing. The signer MUST choose key material that is appropriate
    for the signature's algorithm, and that conforms to any requirements defined by the algorithm, such as key size or format. The
    mechanism by which the signer chooses the algorithm and key material is out of scope for this document.

2. The signer sets the signature's creation time to the current time.

3. If applicable, the signer sets the signature's expiration time property to the time at which the signature is to expire. The expiration is a hint to the verifier, expressing the time at which the signer is no longer willing to vouch for the safety of the signature.

4. The signer creates an ordered set of component identifiers representing the message components to be covered by the signature, and attaches signature metadata parameters to this set. The serialized value of this is later used as the value of the Signature-Input field as described in {{signature-input-header}}.
   * Once an order of covered components is chosen, the order MUST NOT change for the life of the signature.
   * Each covered component identifier MUST be either an HTTP field in the signature context {{http-fields}} or a derived component listed in {{derived-components}} or its associated registry.
   * Signers of a request SHOULD include some or all of the message control data in the covered components, such as the `@method`, `@authority`, `@target-uri`, or some combination thereof.
   * Signers SHOULD include the `created` signature metadata parameter to indicate when the signature was created.
   * The `@signature-params` derived component identifier MUST NOT be listed in the list of covered component identifiers. The derived component is required to always be the last line in the signature base, ensuring that a signature always covers its own metadata and the metadata cannot be substituted.
   * Further guidance on what to include in this set and in what order is out of scope for this document.

5. The signer creates the signature base using these parameters and the signature base creation algorithm. ({{create-sig-input}})

6. The signer uses the `HTTP_SIGN` primitive function to sign the signature base with the chosen signing algorithm using the key material chosen by the signer. The `HTTP_SIGN` primitive and several concrete applications of signing algorithms are defined in in {{signature-methods}}.

7. The byte array output of the signature function is the HTTP message signature output value to be included in the Signature field as defined in {{signature-header}}.

For example, given the HTTP message and signature parameters in the example in {{create-sig-input}}, the example signature base is signed with the `test-key-rsa-pss` key in {{example-key-rsa-pss-test}} and the RSA PSS algorithm described in {{method-rsa-pss-sha512}}, giving the following message signature output value, encoded in Base64:

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

Verification of an HTTP message signature is a process that takes as its input the signature context (including the target message, particularly its Signature and Signature-Input fields) and the requirements for the application. The output of the verification is either a positive verification or an error.

In order to verify a signature, a verifier MUST follow the following algorithm:

1. Parse the Signature and Signature-Input fields as described in {{signature-input-header}} and {{signature-header}}, and extract the signatures to be verified.
    1. If there is more than one signature value present, determine which signature should be processed
        for this message based on the policy and configuration of the verifier. If an applicable signature is not found, produce an error.
    2. If the chosen Signature value does not have a corresponding Signature-Input value,
        produce an error.
2. Parse the values of the chosen Signature-Input field as a parameterized Inner List to get the ordered list of covered components and the signature parameters for the signature to be verified.
3. Parse the value of the corresponding Signature field to get the byte array value of the signature
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
    2. If the algorithm can be determined from the keying material, such as through an algorithm field
        on the key value itself, the verifier will use this algorithm.
    3. If the algorithm is explicitly stated in the signature parameters using a value from the
        HTTP Message Signatures registry, the verifier will use the referenced algorithm.
    4. If the algorithm is specified in more than one location, such as through static configuration
        and the algorithm signature parameter, or the algorithm signature parameter and from
        the key material itself, the resolved algorithms MUST be the same. If the algorithms are
        not the same, the verifier MUST fail the verification.
7. Use the received HTTP message and the parsed signature parameters to re-create the signature base, using
    the algorithm defined in {{create-sig-input}}. The value of the `@signature-params` input is
    the value of the Signature-Input field for this signature serialized according to the rules described
    in {{signature-params}}. Note that this does not include the signature's label from the Signature-Input field.
8. If the key material is appropriate for the algorithm, apply the appropriate `HTTP_VERIFY` cryptographic verification algorithm to the signature,
    recalculated signature base, key material, signature value. The `HTTP_VERIFY` primitive and several concrete algorithms are defined in
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

With the additional requirements that at least the method, authority, path, content-digest, content-length, and content-type be signed, and that the signature creation timestamp is recent enough at the time of verification, the verification passes.

### Enforcing Application Requirements {#verify-requirements}

The verification requirements specified in this document are intended as a baseline set of restrictions that are generally applicable to all use cases. Applications using HTTP Message Signatures MAY impose requirements above and beyond those specified by this document, as appropriate for their use case.

Some non-normative examples of additional requirements an application might define are:

- Requiring a specific set of header fields to be signed (e.g., Authorization, Digest).
- Enforcing a maximum signature age from the time of the `created` time stamp.
- Rejection of signatures past the expiration time in the `expires` time stamp. Note that the expiration time is a hint from the signer and that a verifier can always reject a signature ahead of its expiration time.
- Prohibition of certain signature metadata parameters, such as runtime algorithm signaling with the `alg` parameter when the algorithm is determined from the key information.
- Ensuring successful dereferencing of the `keyid` parameter to valid and appropriate key material.
- Prohibiting the use of certain algorithms, or mandating the use of a specific algorithm.
- Requiring keys to be of a certain size (e.g., 2048 bits vs. 1024 bits).
- Enforcing uniqueness of the `nonce` parameter.
- Requiring an application-specific value for the `tag` parameter.

Application-specific requirements are expected and encouraged. When an application defines additional requirements, it MUST enforce them during the signature verification process, and signature verification MUST fail if the signature does not conform to the application's requirements.

Applications MUST enforce the requirements defined in this document. Regardless of use case, applications MUST NOT accept signatures that do not conform to these requirements.

## Signature Algorithms {#signature-methods}

An HTTP Message signature MUST use a cryptographic digital signature or MAC method that is
appropriate for the key material, environment, and needs of the signer and verifier. This specification does not strictly limit the available signature algorithms, and any signature algorithm that meets these basic requirements MAY be used by an application of HTTP message signatures.

Each signing method `HTTP_SIGN` takes as its input the signature base defined in {{create-sig-input}} as a byte array (`M`), the signing key material
(`Ks`), and outputs the signature output as a byte array (`S`):

~~~
HTTP_SIGN (M, Ks)  ->  S
~~~

Each verification method `HTTP_VERIFY` takes as its input the re-generated signature base defined in {{create-sig-input}} as a byte array (`M`), the verification key
material (`Kv`), and the presented signature to be verified as a byte array (`S`) and outputs the verification result (`V`) as a boolean:

~~~
HTTP_VERIFY (M, Kv, S) -> V
~~~

The following sections contain several common signature algorithms and demonstrates how these cryptographic primitives map to the `HTTP_SIGN` and `HTTP_VERIFY` definitions here. Which method to use can be communicated through the explicit algorithm signature parameter `alg`
defined in {{signature-params}}, by reference to the key material, or through mutual agreement between the signer and verifier. Signature algorithms selected using the `alg` parameter MUST use values from the [HTTP Message Signature Algorithms Registry](#hsa-registry).

### RSASSA-PSS using SHA-512 {#method-rsa-pss-sha512}

To sign using this algorithm, the signer applies the `RSASSA-PSS-SIGN (K, M)` function defined in {{RFC8017}} with the signer's private signing key (`K`) and
the signature base (`M`) ({{create-sig-input}}).
The mask generation function is `MGF1` as specified in {{RFC8017}} with a hash function of SHA-512 {{RFC6234}}.
The salt length (`sLen`) is 64 bytes.
The hash function (`Hash`) SHA-512 {{RFC6234}} is applied to the signature base to create
the digest content to which the digital signature is applied.
The resulting signed content byte array (`S`) is the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `RSASSA-PSS-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key portion of the verification key material (`(n, e)`) and the signature base (`M`) re-created as described in {{verify}}.
The mask generation function is `MGF1` as specified in {{RFC8017}} with a hash function of SHA-512 {{RFC6234}}.
The salt length (`sLen`) is 64 bytes.
The hash function (`Hash`) SHA-512 {{RFC6234}} is applied to the signature base to create the digest content to which the verification function is applied.
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The results of the verification function indicate if the signature presented is valid.

Note that the output of RSA PSS algorithms are non-deterministic, and therefore it is not correct to re-calculate a new signature on the signature base and compare the results to an existing signature. Instead, the verification algorithm defined here needs to be used. See {{security-nondeterministic}}.

Use of this algorithm can be indicated at runtime using the `rsa-pss-sha512` value for the `alg` signature parameter.

### RSASSA-PKCS1-v1_5 using SHA-256 {#method-rsa-v1_5-sha256}

To sign using this algorithm, the signer applies the `RSASSA-PKCS1-V1_5-SIGN (K, M)` function defined in {{RFC8017}} with the signer's private signing key (`K`) and
the signature base (`M`) ({{create-sig-input}}).
The hash SHA-256 {{RFC6234}} is applied to the signature base to create
the digest content to which the digital signature is applied.
The resulting signed content byte array (`S`) is the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `RSASSA-PKCS1-V1_5-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key portion of the verification key material (`(n, e)`) and the signature base (`M`) re-created as described in {{verify}}.
The hash function SHA-256 {{RFC6234}} is applied to the signature base to create the digest content to which the verification function is applied.
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The results of the verification function indicate if the signature presented is valid.

Use of this algorithm can be indicated at runtime using the `rsa-v1_5-sha256` value for the `alg` signature parameter.

### HMAC using SHA-256 {#method-hmac-sha256}

To sign and verify using this algorithm, the signer applies the `HMAC` function {{RFC2104}} with the shared signing key (`K`) and
the signature base (`text`) ({{create-sig-input}}).
The hash function SHA-256 {{RFC6234}} is applied to the signature base to create the digest content to which the HMAC is applied, giving the signature result.

For signing, the resulting value is the HTTP message signature output used in {{sign}}.

For verification, the verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The output of the HMAC function is compared bytewise to the value of the HTTP message signature, and the results of the comparison determine the validity of the signature presented.

Use of this algorithm can be indicated at runtime using the `hmac-sha256` value for the `alg` signature parameter.

### ECDSA using curve P-256 DSS and SHA-256 {#method-ecdsa-p256-sha256}

To sign using this algorithm, the signer applies the `ECDSA` algorithm defined in {{FIPS186-4}} using curve P-256 with the signer's private signing key and
the signature base ({{create-sig-input}}).
The hash SHA-256 {{RFC6234}} is applied to the signature base to create
the digest content to which the digital signature is applied, (`M`).
The signature algorithm returns two integer values, `r` and `s`. These are both encoded as big-endian unsigned integers, zero-padded to 32-octets each. These encoded values are concatenated into a single 64-octet array consisting of the encoded value of `r` followed by the encoded value of `s`. The resulting concatenation of `(r, s)` is byte array of the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `ECDSA` algorithm defined in {{FIPS186-4}}  using the public key portion of the verification key material and the signature base re-created as described in {{verify}}.
The hash function SHA-256 {{RFC6234}} is applied to the signature base to create the digest content to which the signature verification function is applied, (`M`).
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}. This value is a 64-octet array consisting of the encoded values of `r` and `s` concatenated in order. These are both encoded in big-endian unsigned integers, zero-padded to 32-octets each. The resulting signature value `(r, s)` is used as input to the signature verification function.
The results of the verification function indicate if the signature presented is valid.

Note that the output of ECDSA algorithms are non-deterministic, and therefore it is not correct to re-calculate a new signature on the signature base and compare the results to an existing signature. Instead, the verification algorithm defined here needs to be used. See {{security-nondeterministic}}.

Use of this algorithm can be indicated at runtime using the `ecdsa-p256-sha256` value for the `alg` signature parameter.

### ECDSA using curve P-384 DSS and SHA-384 {#method-ecdsa-p384-sha384}

To sign using this algorithm, the signer applies the `ECDSA` algorithm defined in {{FIPS186-4}} using curve P-384 with the signer's private signing key and
the signature base ({{create-sig-input}}).
The hash SHA-384 {{RFC6234}} is applied to the signature base to create
the digest content to which the digital signature is applied, (`M`).
The signature algorithm returns two integer values, `r` and `s`. These are both encoded as big-endian unsigned integers, zero-padded to 48-octets each. These encoded values are concatenated into a single 96-octet array consisting of the encoded value of `r` followed by the encoded value of `s`. The resulting concatenation of `(r, s)` is byte array of the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `ECDSA` algorithm defined in {{FIPS186-4}}  using the public key portion of the verification key material and the signature base re-created as described in {{verify}}.
The hash function SHA-384 {{RFC6234}} is applied to the signature base to create the digest content to which the signature verification function is applied, (`M`).
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}. This value is a 96-octet array consisting of the encoded values of `r` and `s` concatenated in order. These are both encoded in big-endian unsigned integers, zero-padded to 48-octets each. The resulting signature value `(r, s)` is used as input to the signature verification function.
The results of the verification function indicate if the signature presented is valid.

Note that the output of ECDSA algorithms are non-deterministic, and therefore it is not correct to re-calculate a new signature on the signature base and compare the results to an existing signature. Instead, the verification algorithm defined here needs to be used. See {{security-nondeterministic}}.

Use of this algorithm can be indicated at runtime using the `ecdsa-p384-sha384` value for the `alg` signature parameter.

### EdDSA using curve edwards25519 {#method-ed25519}

To sign using this algorithm, the signer applies the `Ed25519` algorithm defined in {{Section 5.1.6 of RFC8032}} with the signer's private signing key and
the signature base ({{create-sig-input}}).
The signature base is taken as the input message (`M`) with no pre-hash function.
The signature is a 64-octet concatenation of `R` and `S` as specified in {{Section 5.1.6 of RFC8032}}, and this is taken as a byte array for the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the signer applies the `Ed25519` algorithm defined in {{Section 5.1.7 of RFC8032}} using the public key portion of the verification key material (`A`) and the signature base re-created as described in {{verify}}.
The signature base is taken as the input message (`M`) with no pre-hash function.
The signature to be verified is processed as the 64-octet concatenation of `R` and `S` as specified in {{Section 5.1.7 of RFC8032}}.
The results of the verification function indicate if the signature presented is valid.

Use of this algorithm can be indicated at runtime using the `ed25519` value for the `alg` signature parameter.

### JSON Web Signature (JWS) algorithms {#method-jose}

If the signing algorithm is a JOSE signing algorithm from the JSON Web Signature and Encryption Algorithms Registry established by {{RFC7518}}, the
JWS algorithm definition determines the signature and hashing algorithms to apply for both signing and verification.

For both signing and verification, the HTTP messages signature base ({{create-sig-input}}) is used as the entire "JWS Signing Input".
The JOSE Header defined in {{RFC7517}} is not used, and the signature base is not first encoded in Base64 before applying the algorithm.
The output of the JWS signature is taken as a byte array prior to the Base64url encoding used in JOSE.

The JWS algorithm MUST NOT be `none` and MUST NOT be any algorithm with a JOSE Implementation Requirement of `Prohibited`.

JWA algorithm values from the JSON Web Signature and Encryption Algorithms Registry are not included as signature parameters. Typically, the JWS algorithm can be signaled using JSON Web Keys or other mechanisms common to JOSE implementations. In fact, and JWA algorithm values are not registered in the [HTTP Message Signature Algorithms Registry](#hsa-registry), and so the explicit `alg` signature parameter is not used at all when using JOSE signing algorithms.

# Including a Message Signature in a Message

HTTP message signatures can be included within an HTTP message via the Signature-Input and Signature fields, both defined within this specification.

The Signature-Input field identifies the covered components and parameters that describe how the signature was generated, while the Signature field contains the signature value. Each field MAY contain multiple labeled values.

An HTTP message signature is identified by a label within an HTTP message. This label MUST be unique within a given HTTP message and MUST be used in both the Signature-Input and Signature fields. The label is chosen by the signer, except where a specific label is dictated by protocol negotiations such as described in {{request-signature}}.

An HTTP message signature MUST use both Signature-Input and Signature fields and each field MUST contain the same labels. The presence of a label in one field but not in the other is an error.

## The Signature-Input HTTP Field {#signature-input-header}

The Signature-Input field is a Dictionary structured field (defined in {{Section 3.2 of STRUCTURED-FIELDS}}) containing the metadata for one or more message signatures generated from components within the HTTP message. Each member describes a single message signature. The member's key is the label that uniquely identifies the message signature within the the HTTP message. The member's value is the serialization of the covered components Inner List plus all signature metadata parameters identified by the label.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig1=("@method" "@target-uri" "@authority" \
  "content-digest" "cache-control");\
  created=1618884475;keyid="test-key-rsa-pss"
~~~

To facilitate signature validation, the Signature-Input field value MUST contain the same serialized value used
in generating the signature base's `@signature-params` value defined in {{signature-params}}. Note that in a structured field value, list order and parameter order have to be preserved.

The signer MAY include the Signature-Input field as a trailer to facilitate signing a message after its content has been processed by the signer. However, since intermediaries are allowed to drop trailers as per {{HTTP}}, it is RECOMMENDED that the Signature-Input field be included only as a header to avoid signatures being inadvertently stripped from a message.

Multiple Signature-Input fields MAY be included in a single HTTP message. The signature labels MUST be unique across all field values.

## The Signature HTTP Field {#signature-header}

The Signature field is a Dictionary structured field defined in {{Section 3.2 of STRUCTURED-FIELDS}} containing one or more message signatures generated from the signature context of the target message. The member's key is the label that uniquely identifies the message signature within the HTTP message. The member's value is a Byte Sequence containing the signature value for the message signature identified by the label.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature: sig1=:P0wLUszWQjoi54udOtydf9IWTfNhy+r53jGFj9XZuP4uKwxyJo\
  1RSHi+oEF1FuX6O29d+lbxwwBao1BAgadijW+7O/PyezlTnqAOVPWx9GlyntiCiHz\
  C87qmSQjvu1CFyFuWSjdGa3qLYYlNm7pVaJFalQiKWnUaqfT4LyttaXyoyZW84jS8\
  gyarxAiWI97mPXU+OVM64+HVBHmnEsS+lTeIsEQo36T3NFf2CujWARPQg53r58Rmp\
  Z+J9eKR2CD6IJQvacn5A4Ix5BUAVGqlyp8JYm+S/CWJi31PNUjRRCusCVRj05NrxA\
  BNFv3r5S9IXf2fYJK+eyW4AiGVMvMcOg==:
~~~

The signer MAY include the Signature field as a trailer to facilitate signing a message after its content has been processed by the signer. However, since intermediaries are allowed to drop trailers as per {{HTTP}}, it is RECOMMENDED that the Signature field be included only as a header to avoid signatures being inadvertently stripped from a message.

Multiple Signature fields MAY be included in a single HTTP message. The signature labels MUST be unique across all field values.

## Multiple Signatures {#signature-multiple}

Multiple distinct signatures MAY be included in a single message. Each distinct signature MUST have a unique label. These multiple signatures could be added all by the same signer or could come from several different signers. For example, a signer may include multiple signatures signing the same message components with different keys or algorithms to support verifiers with different capabilities, or a reverse proxy may include information about the client in fields when forwarding the request to a service host, including a signature over the client's original signature values.

The following non-normative example starts with a signed request from the client. A reverse proxy takes this request and validates the client's signature.

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

The proxy then alters the message before forwarding it on to the origin server, changing the target host and adding the Forwarded header field defined in {{RFC7239}}.

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

The proxy includes the client's signature value from the original message under the label `sig1`, which the proxy signs in addition to the Forwarded field. Note that since the client's signature already covers the client's Signature-Input value for `sig1`, this value is transitively covered by the proxy's signature and need not be added explicitly. The proxy identifies its own key and algorithm and, in this example, includes an expiration for the signature to indicate to downstream systems that the proxy will not vouch for this signed message past this short time window. This results in a signature base of:

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

# Requesting Signatures {#request-signature}

While a signer is free to attach a signature to a request or response without prompting, it is often desirable for a potential verifier to signal that it expects a signature from a potential signer using the Accept-Signature field.

When the Accept-Signature field is sent in an HTTP request message, the field indicates that the client desires the server to sign the response using the identified parameters, and the target message is the response to this request. All responses from resources that support such signature negotiation SHOULD either be uncacheable or contain a Vary header field that lists Accept-Signature, in order to prevent a cache from returning a response with a signature intended for a different request.

When the Accept-Signature field is used in an HTTP response message, the field indicates that the server desires the client to sign its next request to the server with the identified parameters, and the target message is the client's next request. The client can choose to also continue signing future requests to the same server in the same way.

The target message of an Accept-Signature field MUST include all labeled signatures indicated in the Accept-Header signature, each covering the same identified components of the Accept-Signature field.

The sender of an Accept-Signature field MUST include only identifiers that are appropriate for the type of the target message. For example, if the target message is a request, the covered components can not include the `@status` component identifier.

## The Accept-Signature Field {#accept-signature-header}

The Accept-Signature field is a Dictionary structured field (defined in {{Section 3.2 of STRUCTURED-FIELDS}}) containing the metadata for one or more requested message signatures to be generated from message components of the target HTTP message. Each member describes a single message signature. The member's name is a label that uniquely identifies the requested message signature within the context of the target HTTP message. The member's value is the serialization of the desired covered components of the target message, including any allowed signature metadata parameters, using the serialization process defined in {{signature-params}}.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Accept-Signature: sig1=("@method" "@target-uri" "@authority" \
  "content-digest" "cache-control");\
  keyid="test-key-rsa-pss"
~~~

The requested signature MAY include parameters, such as a desired algorithm or key identifier. These parameters MUST NOT include parameters that the signer is expected to generate, such as the `created` parameter.

## Processing an Accept-Signature

The receiver of an Accept-Signature field fulfills that header as follows:

1. Parse the field value as a Dictionary
2. For each member of the dictionary:
    1. The key is taken as the label of the output signature as specified in {{signature-input-header}}
    2. Parse the value of the member to obtain the set of covered component identifiers
    3. Determine that the covered components are applicable to the target message. If not, the process fails and returns an error.
    4. Process the requested parameters, such as the signing algorithm and key material. If any requested parameters cannot be fulfilled, or if the requested parameters conflict with those deemed appropriate to the target message, the process fails and returns an error.
    5. Select and generate any additional parameters necessary for completing the signature
    6. Create the HTTP message signature over the target message
    7. Create the Signature-Input and Signature values and associate them with the label
3. Optionally create any additional Signature-Input and Signature values, with unique labels not found in the Accept-Signature field
4. Combine all labeled Signature-Input and Signature values and attach both fields to the target message

Note that by this process, a signature applied to a target message MUST have the same label, MUST have the same set of covered component, and MAY have additional parameters. Also note that the target message MAY include additional signatures not specified by the Accept-Signature field.

# IANA Considerations {#iana}

IANA is asked to update one registry and create four new registries, according to the following sections.

## HTTP Field Name Registration

IANA is asked to update the
"Hypertext Transfer Protocol (HTTP) Field Name Registry" registry
({{HTTP}}) according to the table below:

|---------------------|-----------|-----------------------------------------------|
| Field Name          | Status    |                     Reference                 |
|---------------------|-----------|-----------------------------------------------|
| Signature-Input     | permanent | {{signature-input-header}} of {{&SELF}}       |
| Signature           | permanent | {{signature-header}} of {{&SELF}}             |
| Accept-Signature    | permanent | {{accept-signature-header}} of {{&SELF}}      |
|---------------------|-----------|-----------------------------------------------|

## HTTP Signature Algorithms Registry {#hsa-registry}

This document defines HTTP Signature Algorithms, for which IANA is asked to create and maintain a new registry titled "HTTP Signature Algorithms". Initial values for this registry are given in {{iana-hsa-contents}}. Future assignments and modifications to existing assignment are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-hsa-template}}.

Algorithms referenced by algorithm identifiers have to be fully defined with all parameters fixed. Algorithm identifiers in this registry are to be interpreted as whole string values and not as a combination of parts. That is to say, it is expected that implementors understand `rsa-pss-sha512` as referring to one specific algorithm with its hash, mask, and salt values set as defined here. Implementors do not parse out the `rsa`, `pss`, and `sha512` portions of the identifier to determine parameters of the signing algorithm from the string, and the registry of one combination of parameters does not imply the registration of other combinations.

Algorithms added to this registry MUST NOT be aliases for other entries in the registry.

### Registration Template {#iana-hsa-template}

{: vspace="0"}
Algorithm Name:
: An identifier for the HTTP Signature Algorithm. The name MUST be an ASCII string consisting only of lower-case characters (`"a"` - `"z"`), digits (`"0"` - `"9"`), and hyphens (`"-"`), and SHOULD NOT exceed 20 characters in length. The identifier MUST be unique within the context of the registry.

Description:
: A brief description of the algorithm used to sign the signature base.

Status:
: A brief text description of the status of the algorithm. The description MUST begin with one of "Active" or "Deprecated", and MAY provide further context or explanation as to the reason for the status.

Specification document(s):
: Reference to the document(s) that specify the
    algorithm, preferably including a URI that can be used
    to retrieve a copy of the document(s). An indication of the
    relevant sections may also be included but is not required.

### Initial Contents {#iana-hsa-contents}

|Algorithm Name|Description|Status|Specification document(s)
|`rsa-pss-sha512`|RSASSA-PSS using SHA-512|Active|{{method-rsa-pss-sha512}} of {{&SELF}}|
|`rsa-v1_5-sha256`|RSASSA-PKCS1-v1_5 using SHA-256|Active|{{method-rsa-v1_5-sha256}} of {{&SELF}}|
|`hmac-sha256`|HMAC using SHA-256|Active|{{method-hmac-sha256}} of {{&SELF}}|
|`ecdsa-p256-sha256`|ECDSA using curve P-256 DSS and SHA-256|Active|{{method-ecdsa-p256-sha256}} of {{&SELF}}|
|`ecdsa-p384-sha384`|ECDSA using curve P-384 DSS and SHA-384|Active|{{method-ecdsa-p384-sha384}} of {{&SELF}}|
|`ed25519`|Edwards Curve DSA using curve edwards25519|Active|{{method-ed25519}} of {{&SELF}}|
{: title="Initial contents of the HTTP Signature Algorithms Registry." }

## HTTP Signature Metadata Parameters Registry {#param-registry}

This document defines the signature parameters structure in {{signature-params}}, which may have parameters containing metadata about a message signature. IANA is asked to create and maintain a new registry titled "HTTP Signature Metadata Parameters" to record and maintain the set of parameters defined for use with member values in the signature parameters structure. Initial values for this registry are given in {{iana-param-contents}}. Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-param-template}}.

### Registration Template {#iana-param-template}

{: vspace="0"}
Name:
: An identifier for the HTTP signature metadata parameter. The name MUST be an ASCII string that conforms to the `key` ABNF rule defined in {{Section 3.1.2 of STRUCTURED-FIELDS}} and SHOULD NOT exceed 20 characters in length. The identifier MUST be unique within the context of the registry.

Description:
: A brief description of the metadata parameter and what it represents.

Specification document(s):
: Reference to the document(s) that specify the
    parameter, preferably including a URI that can be used
    to retrieve a copy of the document(s). An indication of the
    relevant sections may also be included but is not required.


### Initial Contents {#iana-param-contents}

The table below contains the initial contents of the HTTP Signature Metadata Parameters Registry. Each row in the table represents a distinct entry in the registry.

|Name|Description|Specification document(s)|
|--- |--- |--- |
|`alg`|Explicitly declared signature algorithm|{{signature-params}} of {{&SELF}}|
|`created`|Timestamp of signature creation| {{signature-params}} of {{&SELF}}|
|`expires`|Timestamp of proposed signature expiration| {{signature-params}} of {{&SELF}}|
|`keyid`|Key identifier for the signing and verification keys used to create this signature| {{signature-params}} of {{&SELF}}|
|`nonce`|A single-use nonce value| {{signature-params}} of {{&SELF}}|
|`tag`|An application-specific tag for a signature| {{signature-params}} of {{&SELF}}|
{: title="Initial contents of the HTTP Signature Metadata Parameters Registry." }

## HTTP Signature Derived Component Names Registry {#content-registry}

This document defines a method for canonicalizing HTTP message components, including components that can be derived from the context of the target message outside of the HTTP fields. These derived components are identified by a unique string, known as the component name. Component names for derived components always start with the "@" (at) symbol to distinguish them from HTTP field names. IANA is asked to create and maintain a new registry typed "HTTP Signature Derived Component Names" to record and maintain the set of non-field component names and the methods to produce their associated component values. Initial values for this registry are given in {{iana-content-contents}}. Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-content-template}}.

### Registration Template {#iana-content-template}

{: vspace="0"}
Name:
: A name for the HTTP derived component. The name MUST begin with the `"@"` character followed by an ASCII string consisting only of lower-case characters (`"a"` - `"z"`), digits (`"0"` - `"9"`), and hyphens (`"-"`), and SHOULD NOT exceed 20 characters in length. The name MUST be unique within the context of the registry.

Description:
: A description of the derived component.

Status:
: A brief text description of the status of the algorithm. The description MUST begin with one of "Active" or "Deprecated", and MAY provide further context or explanation as to the reason for the status.

Target:
: The valid message targets for the derived parameter. MUST be one of the values "Request", "Response", or "Request, Response". The semantics of these are defined in {{derived-components}}.

Specification document(s):
: Reference to the document(s) that specify the
    derived component, preferably including a URI that can be used
    to retrieve a copy of the document(s). An indication of the
    relevant sections may also be included but is not required.

### Initial Contents {#iana-content-contents}

The table below contains the initial contents of the HTTP Signature Derived Component Names Registry.

|Name|Description|Status|Target|Specification document(s)|
|--- |--- |--- |--- |--- |
|`@signature-params`| Reserved for signature parameters line in signature base | Active | Request, Response | {{signature-params}} of {{&SELF}}|
|`@method`| The HTTP request method | Active | Request | {{content-request-method}} of {{&SELF}}|
|`@authority`| The HTTP authority, or target host | Active | Request | {{content-request-authority}} of {{&SELF}}|
|`@scheme`| The URI scheme of the request URI | Active | Request | {{content-request-scheme}} of {{&SELF}}|
|`@target-uri`| The full target URI of the request | Active | Request | {{content-target-uri}} of {{&SELF}}|
|`@request-target`| The request target of the request | Active | Request | {{content-request-target}} of {{&SELF}}|
|`@path`| The full path of the request URI | Active | Request | {{content-request-path}} of {{&SELF}}|
|`@query`| The full query of the request URI | Active | Request | {{content-request-query}} of {{&SELF}}|
|`@query-param`| A single named query parameter | Active | Request | {{content-request-query-param}} of {{&SELF}}|
|`@status`| The status code of the response | Active | Response | {{content-status-code}} of {{&SELF}}|
{: title="Initial contents of the HTTP Signature Derived Component Names Registry." }

## HTTP Signature Component Parameters Registry {#component-param-registry}

This document defines several kinds of component identifiers, some of which can be parameterized in specific circumstances to provide unique modified behavior. IANA is asked to create and maintain a new registry typed "HTTP Signature Component Parameters" to record and maintain the set of parameters names, the component identifiers they are associated with, and the modifications these parameters make to the component value. Definitions of parameters MUST define the targets to which they apply (such as specific field types, derived components, or contexts) and any incompatibilities with other parameters known at the time of definition. Initial values for this registry are given in {{iana-component-param-contents}}. Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-component-param-template}}.

### Registration Template {#iana-component-param-template}

{: vspace="0"}
Name:
: A name for the parameter. The name MUST be an ASCII string that conforms to the `key` ABNF rule defined in {{Section 3.1.2 of STRUCTURED-FIELDS}} and SHOULD NOT exceed 20 characters in length. The name MUST be unique within the context of the registry.

Description:
: A description of the parameter's function.

Status:
: A brief text description of the status of the parameter. The description MUST begin with one of "Active" or "Deprecated", and MAY provide further context or explanation as to the reason for the status.

Specification document(s):
: Reference to the document(s) that specify the
    derived component, preferably including a URI that can be used
    to retrieve a copy of the document(s). An indication of the
    relevant sections may also be included but is not required.

### Initial Contents {#iana-component-param-contents}

The table below contains the initial contents of the HTTP Signature Derived Component Names Registry.

|Name|Description|Status|Specification document(s)|
|--- |--- |--- |--- |
|`sf`| Strict structured field serialization | Active | {{http-field-structured}} of {{&SELF}}|
|`key`| Single key value of dictionary structured fields | Active | {{http-field-dictionary}} of {{&SELF}}|
|`bs`| Byte Sequence wrapping indicator | Active | {{http-field-byte-sequence}} of {{&SELF}}|
|`tr`| Trailer | Active | {{http-trailer}} of {{&SELF}}|
|`req`| Related request indicator | Active | {{content-request-scheme}} of {{&SELF}}|
|`name`| Single named query parameter | Active | {{content-request-query-param}} of {{&SELF}}|
{: title="Initial contents of the HTTP Signature Component Parameters Registry." }

# Security Considerations {#security}

In order for an HTTP message to be considered _covered_ by a signature, all of the following conditions have to be true:

- a signature is expected or allowed on the message by the verifier
- the signature exists on the message
- the signature is verified against the identified key material and algorithm
- the key material and algorithm are appropriate for the context of the message
- the signature is within expected time boundaries
- the signature covers the expected content, including any critical components
- the list of covered components is applicable to the context of the message

In addition to the application requirement definitions listed in {{application}}, the following security considerations provide discussion and context to the requirements of creating and verifying signatures on HTTP messages.


## General Considerations

### Skipping Signature Verification {#security-ignore}

HTTP Message Signatures only provide security if the signature is verified by the verifier. Since the message to which the signature is attached remains a valid HTTP message without the signature fields, it is possible for a verifier to ignore the output of the verification function and still process the message. Common reasons for this could be relaxed requirements in a development environment or a temporary suspension of enforcing verification during debugging an overall system. Such temporary suspensions are difficult to detect under positive-example testing since a good signature will always trigger a valid response whether or not it has been checked.

To detect this, verifiers should be tested using both valid and invalid signatures, ensuring that the invalid signature fails as expected.

### Use of TLS {#security-tls}

The use of HTTP Message Signatures does not negate the need for TLS or its equivalent to protect information in transit. Message signatures provide message integrity over the covered message components but do not provide any confidentiality for the communication between parties.

TLS provides such confidentiality between the TLS endpoints. As part of this, TLS also protects the signature data itself from being captured by an attacker, which is an important step in preventing [signature replay](#security-replay).

When TLS is used, it needs to be deployed according to the recommendations in {{BCP195}}.

## Message Processing and Selection

### Insufficient Coverage {#security-coverage}

Any portions of the message not covered by the signature are susceptible to modification by an attacker without affecting the signature. An attacker can take advantage of this by introducing or modifying a header field or other message component that will change the processing of the message but will not be covered by the signature. Such an altered message would still pass signature verification, but when the verifier processes the message as a whole, the unsigned content injected by the attacker would subvert the trust conveyed by the valid signature and change the outcome of processing the message.

To combat this, an application of this specification should require as much of the message as possible to be signed, within the limits of the application and deployment. The verifier should only trust message components that have been signed. Verifiers could also strip out any sensitive unsigned portions of the message before processing of the message continues.

### Signature Replay {#security-replay}

Since HTTP Message Signatures allows sub-portions of the HTTP message to be signed, it is possible for two different HTTP messages to validate against the same signature. The most extreme form of this would be a signature over no message components. If such a signature were intercepted, it could be replayed at will by an attacker, attached to any HTTP message. Even with sufficient component coverage, a given signature could be applied to two similar HTTP messages, allowing a message to be replayed by an attacker with the signature intact.

To counteract these kinds of attacks, it's first important for the signer to cover sufficient portions of the message to differentiate it from other messages. In addition, the signature can use the `nonce` signature parameter to provide a per-message unique value to allow the verifier to detect replay of the signature itself if a nonce value is repeated. Furthermore, the signer can provide a timestamp for when the signature was created and a time at which the signer considers the signature to be expired, limiting the utility of a captured signature value.

If a verifier wants to trigger a new signature from a signer, it can send the `Accept-Signature` header field with a new `nonce` parameter. An attacker that is simply replaying a signature would not be able to generate a new signature with the chosen nonce value.

### Choosing Message Components {#security-components}

Applications of HTTP Message Signatures need to decide which message components will be covered by the signature. Depending on the application, some components could be expected to be changed by intermediaries prior to the signature's verification. If these components are covered, such changes would, by design, break the signature.

However, the HTTP Message Signature standard allows for flexibility in determining which components are signed precisely so that a given application can choose the appropriate portions of the message that need to be signed, avoiding problematic components. For example, a web application framework that relies on rewriting query parameters might avoid use of the `@query` derived component in favor of sub-indexing the query value using `@query-param` derived components instead.

Some components are expected to be changed by intermediaries and ought not to be signed under most circumstance. The `Via` and `Forwarded` header fields, for example, are expected to be manipulated by proxies and other middle-boxes, including replacing or entirely dropping existing values. These fields should not be covered by the signature except in very limited and tightly-coupled scenarios.

Additional considerations for choosing signature aspects are discussed in {{application}}.

### Choosing Signature Parameters and Derived Components over HTTP Fields {#security-not-fields}

Some HTTP fields have values and interpretations that are similar to HTTP signature parameters or derived components. In most cases, it is more desirable to sign the non-field alternative. In particular, the following fields should usually not be included in the signature unless the application specifically requires it:

"date"
: The "date" field value represents the timestamp of the HTTP message. However, the creation time of the signature itself is encoded in the `created` signature parameter. These two values can be different, depending on how the signature and the HTTP message are created and serialized. Applications processing signatures for valid time windows should use the `created` signature parameter for such calculations. An application could also put limits on how much skew there is between the "date" field and the `created` signature parameter, in order to limit the application of a generated signature to different HTTP messages. See also {{security-replay}} and {{security-coverage}}.

"host"
: The "host" header field is specific to HTTP/1.1, and its functionality is subsumed by the "@authority" derived component, defined in {{content-request-authority}}. In order to preserve the value across different HTTP versions, applications should always use the "@authority" derived component. See also {{security-versions}}.

### Signature Labels {#security-labels}

HTTP Message Signature values are identified in the Signature and Signature-Input field values by unique labels. These labels are chosen only when attaching the signature values to the message and are not accounted for in the signing process. An intermediary is allowed to re-label an existing signature when processing the message.

Therefore, applications should not rely on specific labels being present, and applications should not put semantic meaning on the labels themselves. Instead, additional signature parameters can be used to convey whatever additional meaning is required to be attached to and covered by the signature. In particular, the `tag` parameter can be used to define an application-specific value as described in {{security-signature-tag}}.

### Multiple Signature Confusion {#security-multiple}

Since [multiple signatures can be applied to one message](#signature-multiple), it is possible for an attacker to attach their own signature to a captured message without modifying existing signatures. This new signature could be completely valid based on the attacker's key, or it could be an invalid signature for any number of reasons. Each of these situations need to be accounted for.

A verifier processing a set of valid signatures needs to account for all of the signers, identified by the signing keys. Only signatures from expected signers should be accepted, regardless of the cryptographic validity of the signature itself.

A verifier processing a set of signatures on a message also needs to determine what to do when one or more of the signatures are not valid. If a message is accepted when at least one signature is valid, then a verifier could drop all invalid signatures from the request before processing the message further. Alternatively, if the verifier rejects a message for a single invalid signature, an attacker could use this to deny service to otherwise valid messages by injecting invalid signatures alongside the valid ones.

### Collision of Application-Specific Signature Tag {#security-signature-tag}

Multiple applications and protocols could apply HTTP signatures on the same message simultaneously. In fact, this is a desired feature in many circumstances as described in {{signature-multiple}}. A naive verifier could become confused in processing multiple signatures, either accepting or rejecting a message based on an unrelated or irrelevant signature. In order to help an application select which signatures apply to its own processing, the application can declare a specific value for the `tag` signature parameter as defined in {{signature-params}}. For example, a signature targeting an application gateway could require `tag="app-gateway"` as part of the signature parameters for that application.

The use of the `tag` parameter does not prevent an attacker from also using the same value as a target application, since the parameter's value is public and otherwise unrestricted. As a consequence, a verifier should only use value of the `tag` parameter to limit which signatures to check. Each signature still needs to be examined by the verifier to ensure that sufficient coverage is provided, as discussed in {{security-coverage}}.

### Message Content {#security-message-content}

On its own, this specification does not provide coverage for the content of an HTTP message under the signature, either in request or response. However, {{DIGEST}} defines a set of fields that allow a cryptographic digest of the content to be represented in a field. Once this field is created, it can be included just like any other field as defined in {{http-fields}}.

For example, in the following response message:

~~~ http-message
HTTP/1.1 200 OK
Content-Type: application/json

{"hello": "world"}
~~~

The digest of the content can be added to the Content-Digest field as follows:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

HTTP/1.1 200 OK
Content-Type: application/json
Content-Digest: \
  sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:

{"hello": "world"}
~~~

This field can be included in a signature base just like any other field along with the basic signature parameters:

~~~
"@status": 200
"content-digest": \
  sha-256=:X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=:
"@signature-input": ("@status" "content-digest")
~~~

From here, the signing process proceeds as usual.

Upon verification, it is important that the verifier validate not only the signature but also the value of the Content-Digest field itself against the actual received content. Unless the verifier performs this step, it would be possible for an attacker to substitute the message content but leave the Content-Digest field value untouched to pass the signature. Since only the field value is covered by the signature directly, checking only the signature is not sufficient protection against such a substitution attack.

As discussed in {{DIGEST}}, the value of the Content-Digest field is dependent on the content encoding of the message. If an intermediary changes the content encoding, the resulting Content-Digest value would change, which would in turn invalidate the signature. Any intermediary performing such an action would need to apply a new signature with the updated Content-Digest field value, similar to the reverse proxy use case discussed in {{signature-multiple}}.

## Cryptographic Considerations

### Cryptography and Signature Collision {#security-collision}

The HTTP Message Signatures specification does not define any of its own cryptographic primitives, and instead relies on other specifications to define such elements. If the signature algorithm or key used to process the signature base is vulnerable to any attacks, the resulting signature will also be susceptible to these same attacks.

A common attack against signature systems is to force a signature collision, where the same signature value successfully verifies against multiple different inputs. Since this specification relies on reconstruction of the signature base from an HTTP message, and the list of components signed is fixed in the signature, it is difficult but not impossible for an attacker to effect such a collision. An attacker would need to manipulate the HTTP message and its covered message components in order to make the collision effective.

To counter this, only vetted keys and signature algorithms should be used to sign HTTP messages. The HTTP Message Signatures Algorithm Registry is one source of trusted signature algorithms for applications to apply to their messages.

While it is possible for an attacker to substitute the signature parameters value or the signature value separately, the [signature base generation algorithm](#create-sig-input) always covers the signature parameters as the final value in the signature base using a deterministic serialization method. This step strongly binds the signature base with the signature value in a way that makes it much more difficult for an attacker to perform a partial substitution on the signature bases.

### Key Theft {#security-keys}

A foundational assumption of signature-based cryptographic systems is that the signing key is not compromised by an attacker. If the keys used to sign the message are exfiltrated or stolen, the attacker will be able to generate their own signatures using those keys. As a consequence, signers have to protect any signing key material from exfiltration, capture, and use by an attacker.

To combat this, signers can rotate keys over time to limit the amount of time stolen keys are useful. Signers can also use key escrow and storage systems to limit the attack surface against keys. Furthermore, the use of asymmetric signing algorithms exposes key material less than the use of [symmetric signing algorithms](#security-symmetric).

### Symmetric Cryptography {#security-symmetric}

The HTTP Message Signatures specification allows for both asymmetric and symmetric cryptography to be applied to HTTP messages. By its nature, symmetric cryptographic methods require the same key material to be known by both the signer and verifier. This effectively means that a verifier is capable of generating a valid signature, since they have access to the same key material. An attacker that is able to compromise a verifier would be able to then impersonate a signer.

Where possible, asymmetric methods or secure key agreement mechanisms should be used in order to avoid this type of attack. When symmetric methods are used, distribution of the key material needs to be protected by the overall system. One technique for this is the use of separate cryptographic modules that separate the verification process (and therefore the key material) from other code, minimizing the vulnerable attack surface. Another technique is the use of key derivation functions that allow the signer and verifier to agree on unique keys for each message without having to share the key values directly.

Additionally, if symmetric algorithms are allowed within a system, special care must be taken to avoid [key downgrade attacks](#security-keydowngrade).

### Key Specification Mix-Up {#security-keymixup}

The existence of a valid signature on an HTTP message is not sufficient to prove that the message has been signed by the appropriate party. It is up to the verifier to ensure that a given key and algorithm are appropriate for the message in question. If the verifier does not perform such a step, an attacker could substitute their own signature using their own key on a message and force a verifier to accept and process it. To combat this, the verifier needs to ensure that not only does the signature validate for a message, but that the key and algorithm used are appropriate.

### Non-deterministic Signature Primitives {#security-nondeterministic}

Some cryptographic primitives such as RSA PSS and ECDSA have non-deterministic outputs, which include some amount of entropy within the algorithm. For such algorithms, multiple signatures generated in succession will not match. A lazy implementation of a verifier could ignore this distinction and simply check for the same value being created by re-signing the signature base. Such an implementation would work for deterministic algorithms such as HMAC and EdDSA but fail to verify valid signatures made using non-deterministic algorithms. It is therefore important that a verifier always use the correctly-defined verification function for the algorithm in question and not do a simple comparison.

### Key and Algorithm Specification Downgrades {#security-keydowngrade}

Applications of this specification need to protect against key specification downgrade attacks. For example, the same RSA key can be used for both RSA-PSS and RSA v1.5 signatures. If an application expects a key to only be used with RSA-PSS, it needs to reject signatures for that key using the weaker RSA 1.5 specification.

Another example of a downgrade attack occurs when an asymmetric algorithm is expected, such as RSA-PSS, but an attacker substitutes a signature using symmetric algorithm, such as HMAC. A naive verifier implementation could use the value of the public RSA key as the input to the HMAC verification function. Since the public key is known to the attacker, this would allow the attacker to create a valid HMAC signature against this known key. To prevent this, the verifier needs to ensure that both the key material and the algorithm are appropriate for the usage in question. Additionally, while this specification does allow runtime specification of the algorithm using the `alg` signature parameter, applications are encouraged to use other mechanisms such as static configuration or higher protocol-level algorithm specification instead, preventing an attacker from substituting the algorithm specified.

## Matching Covered Components to Message

### Modification of Required Message Parameters {#security-modify}

An attacker could effectively deny a service by modifying an otherwise benign signature parameter or signed message component. While rejecting a modified message is the desired behavior, consistently failing signatures could lead to the verifier turning off signature checking in order to make systems work again (see {{security-ignore}}), or to the application minimizing the signed component requirements.

If such failures are common within an application, the signer and verifier should compare their generated signature bases with each other to determine which part of the message is being modified. If an expected modification is found, the signer and verifier can agree on an alternative set of requirements that will pass. However, the signer and verifier should not remove the requirement to sign the modified component when it is suspected an attacker is modifying the component.

### Mismatch of Signature Parameters from Message {#security-mismatch}

The verifier needs to make sure that the signed message components match those in the message itself. For example, the `@method` derived component requires that the value within the signature base be the same as the HTTP method used when presenting this message. This specification encourages this by requiring the verifier to derive the signature base from the message, but lazy cacheing or conveyance of a raw signature base to a processing subsystem could lead to downstream verifiers accepting a message that does not match the presented signature.

To counter this, the component that generates the signature base needs to be trusted by both the signer and verifier within a system.

### Message Component Source and Context {#security-message-component-context}

The signature context for deriving message component values includes the target HTTP Message itself, any associated messages (such as the request that triggered a response), and additional information that the signer or verifier has access to. Both signers and verifiers need to take carefully consider the source of all information when creating component values for the signature base and take care not to take information from untrusted sources. Otherwise, an attacker could leverage such a loosely-defined message context to inject their own values into the signature base string, overriding or corrupting the intended values.

For example, in most situations, the target URI of the message is defined in {{HTTP, Section 7.1}}. However, let's say that there is an application that requires signing of the `@authority` of the incoming request, but the application doing the processing is behind a reverse proxy. Such an application would expect a change in the `@authority` value, and it could be configured to know the external target URI as seen by the client on the other side of the proxy. This application would use this configured value as its target URI for the purposes of deriving message component values such as `@authority` instead of using the target URI of the incoming message.

This approach is not without problems, as a misconfigured system could accept signed requests intended for different components in the system. For this scenario, an intermediary could instead add its own signature to be verified by the application directly, as demonstrated in {{signature-multiple}}. This alternative approach requires a more active intermediary but relies less on the target application knowing external configuration values.

For another example, {{content-request-response}} defines a method for signing response messages but including portions of the request message that triggered the response. In this case, the context for component value calculation is the combination of the response and request message, not just the single message to which the signature is applied. For this feature, the `req` flag allows both signer to explicitly signal which part of the context is being sourced for a component identifier's value. Implementations need to ensure that only the intended message is being referred to for each component, otherwise an attacker could attempt to subvert a signature by manipulating one side or the other.

### Multiple Message Component Contexts {#security-context-multiple-signatures}

It is possible that the context for deriving message component values could be distinct for each signature present within a single message. This is particularly the case when proxies mutate messages and include signatures over the mutated values, in addition to any existing signatures. For example, a reverse proxy can replace a public hostname in a request to a service with the hostname for the individual service host that it is forwarding the request on to. If both the client and the reverse proxy add signatures covering `@authority`, the service host will see two signatures on the request, each signing different values for the `@authority` message component, reflecting the change to that component as the message made its way from the client to the service host.

In such a case, it's common for the internal service to verify only one of the signatures or to use externally-configured information, as discussed in {{security-message-component-context}}. However, a verifier processing both signatures has to use a different message component context for each signature, since the component value for the `@authority` component will be different for each signature. Verifiers like this need to be aware of both the reverse proxy's context for incoming messages as well as the target service's context for the message coming from the reverse proxy. The verifier needs to take particular care to apply the correct context to the correct signature, otherwise an attacker could use knowledge of this complex setup to confuse the inputs to the verifier.

Such verifiers also need to ensure that any differences in message component contexts between signatures are expected and permitted. For example, in the above scenario, the reverse proxy could include the original hostname in a `Forwarded` header field, and sign `@authority`, `forwarded`, and the client's entry in the `signature` field. The verifier can use the hostname from the `Forwarded` header field to confirm that the hostname was transformed as expected.


## HTTP Processing

### Confusing HTTP Field Names for Derived Component Names {#security-lazy-header-parser}

The definition of HTTP field names does not allow for the use of the `@` character anywhere in the name. As such, since all derived component names start with the `@` character, these namespaces should be completely separate. However, some HTTP implementations are not sufficiently strict about the characters accepted in HTTP field names. In such implementations, a sender (or attacker) could inject a header field starting with an `@` character and have it passed through to the application code. These invalid header fields could be used to override a portion of the derived message content and substitute an arbitrary value, providing a potential place for an attacker to mount a [signature collision](#security-collision) attack or other functional substitution attack (such as using the signature from a GET request on a crafted POST request).

To combat this, when selecting values for a message component, if the component name starts with the `@` character, it needs to be processed as a derived component and never taken as a fields. Only if the component name does not start with the `@` character can it be taken from the fields of the message. The algorithm discussed in {{create-sig-input}} provides a safe order of operations.

### Semantically Equivalent Field Values {#security-field-values}

The [signature base generation algorithm](#create-sig-input) uses the value of an HTTP field as its component value. In the common case, this amounts to taking the actual bytes of the field value as the component value for both the signer and verifier. However, some field values allow for transformation of the values in semantically equivalent ways that alter the bytes used in the value itself. For example, a field definition can declare some or all of its value to be case-insensitive, or to have special handling of internal whitespace characters. Other fields have expected transformations from intermediaries, such as the removal of comments in the `Via` header field. In such cases, a verifier could be tripped up by using the equivalent transformed field value, which would differ from the byte value used by the signer. The verifier would have have a difficult time finding this class of errors since the value of the field is still acceptable for the application, but the actual bytes required by the signature base would not match.

When processing such fields, the signer and verifier have to agree how to handle such transformations, if at all. One option is to not sign problematic fields, but care must be taken to ensure that there is still [sufficient signature coverage](#security-coverage) for the application. Another option is to define an application-specific canonicalization value for the field before it is added to the HTTP message, such as to always remove internal comments before signing, or to always transform values to lowercase. Since these transformations are applied prior to the field being used as input to the signature base generation algorithm, the signature base will still simply contain the byte value of the field as it appears within the message. If the transformations were to be applied after the value is extracted from the message but before it is added to the signature base, different attack surfaces such as value substitution attacks could be launched against the application. All application-specific additional rules are outside the scope of this specification, and by their very nature these transformations would harm interoperability of the implementation outside of this specific application. It is recommended that applications avoid the use of such additional rules wherever possible.

### Parsing Structured Field Values {#security-structured}

Several parts of this specification rely on the parsing of structured field values {{STRUCTURED-FIELDS}}. In particular, [normalization of HTTP structured field values](#http-field-structured), [referencing members of a dictionary structured field](#http-field-dictionary), and processing the `@signature-input` value when [verifying a signature](#verify). While structured field values are designed to be relatively simple to parse, a naive or broken implementation of such a parser could lead to subtle attack surfaces being exposed in the implementation.

For example, if a buggy parser of the `@signature-input` value does not enforce proper closing of quotes around string values within the list of component identifiers, an attacker could take advantage of this and inject additional content into the signature base through manipulating the Signature-Input field value on a message.

To counteract this, implementations should use fully compliant and trusted parsers for all structured field processing, both on the signer and verifier side.

### HTTP Versions and Component Ambiguity {#security-versions}

Some message components are expressed in different ways across HTTP versions. For example, the authority of the request target is sent using the `Host` header field in HTTP/1.1 but with the `:authority` pseudo-header in HTTP/2. If a signer sends an HTTP/1.1 message and signs the `Host` field, but the message is translated to HTTP/2 before it reaches the verifier, the signature will not validate as the `Host` header field could be dropped.

It is for this reason that HTTP Message Signatures defines a set of derived components that define a single way to get value in question, such as the `@authority` derived component ({{content-request-authority}}) in lieu of the `Host` header field. Applications should therefore prefer derived components for such options where possible.

### Canonicalization Attacks {#security-canonicalization}

Any ambiguity in the generation of the signature base could provide an attacker with leverage to substitute or break a signature on a message. Some message component values, particularly HTTP field values, are potentially susceptible to broken implementations that could lead to unexpected and insecure behavior. Naive implementations of this specification might implement HTTP field processing by taking the single value of a field and using it as the direct component value without processing it appropriately.

For example, if the handling of `obs-fold` field values does not remove the internal line folding and whitespace, additional newlines could be introduced into the signature base by the signer, providing a potential place for an attacker to mount a [signature collision](#security-collision) attack. Alternatively, if header fields that appear multiple times are not joined into a single string value, as is required by this specification, similar attacks can be mounted as a signed component value would show up in the signature base more than once and could be substituted or otherwise attacked in this way.

To counter this, the entire field value processing algorithm needs to be implemented by all implementations of signers and verifiers.

### Non-List Field Values {#security-non-list}

When an HTTP field occurs multiple times in a single message, these values need to be combined into a single one-line string value to be included in the HTTP signature base, as described in {{create-sig-input}}. Not all HTTP fields can be combined into a single value in this way and still be a valid value for the field. For the purposes of generating the signature base, the message component value is never meant to be read back out of the signature base string or used in the application. Therefore it is considered best practice to treat the signature base generation algorithm separately from processing the field values by the application, particularly for fields that are known to have this property. If the field values that are being signed do not validate, the signed message should also be rejected.

If an HTTP field allows for unquoted commas within its values, combining multiple field values can lead to a situation where two semantically different messages produce the same line in a signature base. For example, take the following hypothetical header field with an internal comma in its syntax, here used to define two separate lists of values:

~~~ http-message
Example-Header: value, with, lots
Example-Header: of, commas
~~~

For this header field, sending all of these values as a single field value results in a single list of values:

~~~ http-message
Example-Header: value, with, lots, of, commas
~~~

Both of these messages would create the following line in the signature base:

~~~
"example-header": value, with, lots, of, commas
~~~

Since two semantically distinct inputs can create the same output in the signature base, special care has to be taken when handling such values.

Specifically, the Set-Cookie field {{COOKIE}} defines an internal syntax that does not conform to the List syntax in {{STRUCTURED-FIELDS}}. In particular some portions allow unquoted commas, and the field is typically sent as multiple separate field lines with distinct values when sending multiple cookies. When multiple Set-Cookie fields are sent in the same message, it is not generally possible to combine these into a single line and be able to parse and use the results, as discussed in {{HTTP, Section 5.3}}. Therefore, all the cookies need to be processed from their separate header values, without being combined, while the signature base needs to be processed from the special combined value generated solely for this purpose. If the cookie value is invalid, the signed message ought to be rejected as this is a possible padding attack as described in {{security-multiple-fields}}.

To deal with this, an application can choose to limit signing of problematic fields like Set-Cookie, such as including the field in a signature only when a single field value is present and the results would be unambiguous. Similar caution needs to be taken with all fields that could have non-deterministic mappings into the signature base. Signers can also make use of the `bs` parameter to armor such fields, as described in {{http-field-byte-sequence}}.

### Padding Attacks with Multiple Field Values {#security-multiple-fields}

Since HTTP field values need to be combined in a single string value to be included in the HTTP signature base, as described in {{create-sig-input}}, it is possible for an attacker to inject an additional value for a given field and add this to the signature base of the verifier.

In most circumstances, this causes the signature validation to fail as expected, since the new signature base value will not match the one used by the signer to create the signature. However, it is theoretically possible for the attacker to inject both a garbage value to a field and a desired value to another field in order to force a particular input. This is a variation of the collision attack described in {{security-collision}}, where the attacker accomplishes their change in the message by adding to existing field values.

To counter this, an application needs to validate the content of the fields covered in the signature in addition to ensuring that the signature itself validates. With such protections, the attacker's padding attack would be rejected by the field value processor, even in the case where the attacker could force a signature collision.


# Privacy Considerations {#privacy}

## Identification through Keys {#privacy-identify-keys}

If a signer uses the same key with multiple verifiers, or uses the same key over time with a single verifier, the ongoing use of that key can be used to track the signer throughout the set of verifiers that messages are sent to. Since cryptographic keys are meant to be functionally unique, the use of the same key over time is a strong indicator that it is the same party signing multiple messages.

In many applications, this is a desirable trait, and it allows HTTP Message Signatures to be used as part of authenticating the signer to the verifier. However, it could be unintentional tracking that a signer might not be aware of. To counter this kind of tracking, a signer can use a different key for each verifier that it is in communication with. Sometimes, a signer could also rotate their key when sending messages to a given verifier. These approaches do not negate the need for other anti-tracking techniques to be applied as necessary.

## Signatures do not provide confidentiality {#privacy-confidentiality}

HTTP Message Signatures do not provide confidentiality of any of the information protected by the signature. The content of the HTTP message, including the value of all fields and the value of the signature itself, is presented in plaintext to any party with access to the message.

To provide confidentiality at the transport level, TLS or its equivalent can be used as discussed in {{security-tls}}.

## Oracles {#privacy-oracle}

It is important to balance the need for providing useful feedback to developers on error conditions without providing additional information to an attacker. For example, a naive but helpful server implementation might try to indicate the required key identifier needed for requesting a resource. If someone knows who controls that key, a correlation can be made between the resource's existence and the party identified by the key. Access to such information could be used by an attacker as a means to target the legitimate owner of the resource for further attacks.

## Required Content {#privacy-required}

A core design tenet of this specification is that all message components covered by the signature need to be available to the verifier in order to recreate the signature base and verify the signature. As a consequence, if an application of this specification requires that a particular field be signed, the verifier will need access to the value of that field.

For example, in some complex systems with intermediary processors this could cause the surprising behavior of an intermediary not being able to remove privacy-sensitive information from a message before forwarding it on for processing, for fear of breaking the signature. A possible mitigation for this specific situation would be for the intermediary to verify the signature itself, then modifying the message to remove the privacy-sensitive information. The intermediary can add its own signature at this point to signal to the next destination that the incoming signature was validated, as is shown in the example in {{signature-multiple}}.

--- back

# Detecting HTTP Message Signatures {#detection}

There have been many attempts to create signed HTTP messages in the past, including other non-standardized definitions of the Signature field, which is used within this specification. It is recommended that developers wishing to support both this specification and other historical drafts do so carefully and deliberately, as incompatibilities between this specification and various versions of other drafts could lead to unexpected problems.

It is recommended that implementers first detect and validate the Signature-Input field defined in this specification to detect that this standard is in use and not an alternative. If the Signature-Input field is present, all Signature fields can be parsed and interpreted in the context of this specification.

# Examples

The following non-normative examples are provided as a means of testing implementations of HTTP Message Signatures. The signed messages given can be used to create the signature base with the stated parameters, creating signatures using the stated algorithms and keys.

The private keys given can be used to generate signatures, though since several of the demonstrated algorithms are nondeterministic, the results of a signature are expected to be different from the exact bytes of the examples. The public keys given can be used to validate all signed examples.

## Example Keys {#example-keys}

This section provides cryptographic keys that are referenced in example signatures throughout this document. These keys MUST NOT be used for any purpose other than testing.

The key identifiers for each key are used throughout the examples in this specification. It is assumed for these examples that the signer and verifier can unambiguously dereference all key identifiers used here, and that the keys and algorithms used are appropriate for the context in which the signature is presented.

The components for each private key in PEM format can be displayed by executing the following OpenSSL command:

~~~
openssl pkey -text
~~~

This command was tested with all the example keys on OpenSSL version 1.1.1m. Note that some systems cannot produce or use all of these keys directly, and may require additional processing. All keys are also made available in JWK format.

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

The same public and private keypair in JWK format:

~~~json
NOTE: '\' line wrapping per RFC 8792

{
  "kty": "RSA",
  "kid": "test-key-rsa",
  "p": "sqeUJmqXE3LP8tYoIjMIAKiTm9o6psPlc8CrLI9CH0UbuaA2JCOMcCNq8Sy\
  YbTqgnWlB9ZfcAm_cFpA8tYci9m5vYK8HNxQr-8FS3Qo8N9RJ8d0U5CswDzMYfRgh\
  AfUGwmlWj5hp1pQzAuhwbOXFtxKHVsMPhz1IBtF9Y8jvgqgYHLbmyiu1mw",
  "q": "vSlgXQbvHzWmuUBFRHAejRh_naQTDV3GnH4lcRHuFBFZCSLn82xQS2_7xFO\
  qfabqq17kNcvKfzdvWpGxxJ2cILAq0pZS6DmrZlvBU4IkK2ZHCac_XfWVZFh-PrsH\
  _EnVkDpfcYR_iw1F40C1q5w8R6WBHaew3SAp",
  "d": "b8lm5JZ2hUduLnq-OAKCSODeWQ7Uqs7eet2bqeuAD0_2po-PG4qhZoo7VwF\
  CUTWlJan9wqdxiAPlbEQKkCdFRcbakbjN2TMJjMCHWL5zfgvqhmgeyKsrqg1wSce9\
  7J1_Mkvn3fh6CbqnwNb6bVFDvTJS3i5FzRhKiv6rUsYm8ZAdF4XRaYkFkeuHPl7rc\
  -ruUTSAjC4GovxIxoDJFe0r4kbFmkiZOr40e8RZYK7T1IKrSvzfxx5AjnlK_OZOTC\
  q0L7wBPbMW-IxmQpFCjpI-yuoi3FlZG3LaLNrBMXQF_lLZUDHs77q3fAGxDWwum2h\
  KBfdBuUQtjlqwjQlgXPsskQ",
  "e": "AQAB",
  "qi": "PkbARLOwU_LcZrQy9mmfcPoQlAuCyeu1Q9nH7PYSnbHTFzmiud4Hl8bIXU\
  9a0_58blDoOl3PctF-b4rAEJYUpCODu5PFyN6uEFYRg-YQwpjBMkXk8Eb39128ctA\
  RB40Lx8caDhRdTyaEedIG3cQDXSpAl9EOzXkzfx4bZxjAHU9mkMdJwOcMDQ",
  "dp": "aiodZsrWpi8HFfZfeRs8OS_0L5x6WBl3Y9btoZgsIeruc9uZ8NXTIdxaM6\
  FdnyNEyOYA1VH94tDYR-xEt1br1ud_dkPslLV_Aac7d7EaYc7cdkb7oC9t6sphVg0\
  dqE0UTDlOwBxBYMtGmQbJsFzGpmjzVgKqWqJ3B947li2U7t63HXEvKprY2w",
  "dq": "b0DzpSMb5p42dcQgOTU8Mr4S6JOEhRr_YjErMkpaXUEqvZ3jEB9HRmcRi5\
  Gtt4NBiBMiY6V9br8a5gjEpiAQoIUcWokBMAYjEeurU8M6JLBd3YaZVVjISaFmdty\
  nwLFoQxCh6_EC1rSywwrfDpSwO29S9i8Xbaap",
  "n": "hAKYdtoeoy8zcAcR874L8cnZxKzAGwd7v36APp7Pv6Q2jdsPBRrwWEBnez6\
  d0UDKDwGbc6nxfEXAy5mbhgajzrw3MOEt8uA5txSKobBpKDeBLOsdJKFqMGmXCQvE\
  G7YemcxDTRPxAleIAgYYRjTSd_QBwVW9OwNFhekro3RtlinV0a75jfZgkne_YiktS\
  vLG34lw2zqXBDTC5NHROUqGTlML4PlNZS5Ri2U4aCNx2rUPRcKIlE0PuKxI4T-HIa\
  Fpv8-rdV6eUgOrB2xeI1dSFFn_nnv5OoZJEIB-VmuKn3DCUcCZSFlQPSXSfBDiUGh\
  wOw76WuSSsf1D4b_vLoJ10w"
}
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

The same public and private keypair in JWK format:

~~~json
NOTE: '\' line wrapping per RFC 8792

{
  "kty": "RSA",
  "kid": "test-key-rsa-pss",
  "p": "5V-6ISI5yEaCFXm-fk1EM2xwAWekePVCAyvr9QbTlFOCZwt9WwjUjhtKRus\
  i5Uq-IYZ_tq2WRE4As4b_FHEMtp2AER43IcvmXPqKFBoUktVDS7dThIHrsnRi1U7d\
  HqVdwiMEMe5jxKNgnsKLpnq-4NyhoS6OeWu1SFozG9J9xQk",
  "q": "w-wIde17W5Y0Cphp3ZZ0uM8OUq1AkrV2IKauqYHaDxAT32EM4ci2MMER2nI\
  UEo4g_42lW0zYouFFqONwv0-HyOsgPpdSqKRC5WLgn0VXabjaNcy6KhNPXeJ0Agtq\
  diDwPeJ2_L_eKwNWQ43RfdQBUquAwSd7SEmmQ8sViqB628M",
  "d": "lAfIqfpCYomVShfAKnwf2lD9I0wKjkHsCtZCif4kAlwQqqW6N-tIL3bdOR-\
  VWf0Q1ZBIDtpO91UrG7pansyrPERbNrRJlPiYEyPTHkCT1nD-l2isuiyGLNBNnFoK\
  fBgA4KAbPJZQatFIV9Cn34JSHnpN5-2ehreGBYHtkwHFtlmzeF3yu5bqRcqOhx8lk\
  YmBzDAEUFyyXjknU5-WjAT9DzuG0MpOTkcU1EnjnIjyVBZLUB5Lxm8puyq8hH8B_E\
  5LNC-1oc8j-tDy98UvRTTiYvZvs87cGCFxg0LijNhg7CE3g9piNqB6DzMgA9MHSOw\
  cElVtfKdYfo4H3OHZXsSmEQ",
  "e": "AQAB",
  "qi": "jRAqfYi_tKCjhP9eM0N2XaRlNeoYCTx06GlSLD8d0zc4ZZuEePY10LMGWI\
  6Y_JC0CvvvQYhNa9sAj4hFjIVLsWeTplVVUezGO1ofLW4kYWVpnMpHgAY1pRM4kyz\
  o1p3MKYY8DE1BA4KqhSOfhdGs6Ov3Dfj0migZeE7Fu7yc7Fc",
  "dp": "otDolkxtJ7Sk8gmRJqZCGx6GAvlGznWJfibXPv6xgUAl-G83dD84YgcNGn\
  oeMxRzEekfDtT5LVMRPF4_AoucsqPqHDyOdfb-dlGBYfOBVxj6w-xF5HE0lV_4J-H\
  rI63Od9fTSn4lY5d1JjyCVJIcnBEAyiD6EUZbUBh23vDzRcE",
  "dq": "iZE1S6CpqmBoQDxOsXGQmaeBdhoCqkDSJhEDuS_dLhBq88FQa0UkcE1QvO\
  K3J2Q21VnfDqGBx7SH1hOFOj-cpz45kNluB832ztxDvnHQ9AIA7h_HY_3VD6YPMNR\
  VN4bfSYS3abdLR0Z7jsmInGJ9X0_fA0E2tkZIgXeas5EFU0M",
  "n": "r4tmm3r20Wd_PbqvP1s2-QEtvpuRaV8Yq40gjUR8y2Rjxa6dpG2GXHbPfvM\
  s8ct-Lh1GH45x28Rw3Ry53mm-oAXjyQ86OnDkZ5N8lYbggD4O3w6M6pAvLkhk95An\
  dTrifbIFPNU8PPMO7OyrFAHqgDsznjPFmTOtCEcN2Z1FpWgchwuYLPL-Wokqltd11\
  nqqzi-bJ9cvSKADYdUAAN5WUtzdpiy6LbTgSxP7ociU4Tn0g5I6aDZJ7A8Lzo0KSy\
  ZYoA485mqcO0GVAdVw9lq4aOT9v6d-nb4bnNkQVklLQ3fVAvJm-xdDOp9LCNCN48V\
  2pnDOkFV6-U9nV5oyc6XI2w"
}
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

The same public and private keypair in JWK format:

~~~json
{
  "kty": "EC",
  "crv": "P-256",
  "kid": "test-key-ecc-p256",
  "d": "UpuF81l-kOxbjf7T4mNSv0r5tN67Gim7rnf6EFpcYDs",
  "x": "qIVYZVLCrPZHGHjP17CTW0_-D9Lfw0EkjqF7xB4FivA",
  "y": "Mc4nN9LTDOBhfoUeg8Ye9WedFRhnZXZJA12Qp0zZ6F0"
}
~~~

### Example Ed25519 Test Key {#example-key-ed25519}

The following key is an elliptical curve key over the Edwards curve ed25519, referred to in this document as `test-key-ed25519`. This key is PCKS#8 encoded in PEM format, with no encryption.

~~~
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAJrQLj5P/89iXES9+vFgrIy29clF9CC/oPPsw3c5D0bs=
-----END PUBLIC KEY-----

-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIJ+DYvh6SEqVTm50DFtMDoQikTmiCqirVv9mWG9qfSnF
-----END PRIVATE KEY-----
~~~

The same public and private keypair in JWK format:

~~~json
{
  "kty": "OKP",
  "crv": "Ed25519",
  "kid": "test-key-ed25519",
  "d": "n4Ni-HpISpVObnQMW0wOhCKROaIKqKtW_2ZYb2p9KcU",
  "x": "JrQLj5P_89iXES9-vFgrIy29clF9CC_oPPsw3c5D0bs"
}
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
NOTE: '\' line wrapping per RFC 8792

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
NOTE: '\' line wrapping per RFC 8792

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

The corresponding signature base is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@signature-params": ();created=1618884473;keyid="test-key-rsa-pss"\
  ;nonce="b3k2pp5k7z-50gnwp.yemd"
~~~

This results in the following Signature-Input and Signature header fields being added to the message under the signature label `sig-b21`:

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

This example covers additional components (the authority, the Content-Digest header field, and a single named query parameter) in `test-request` using the `rsa-pss-sha512` algorithm. This example also adds a `tag` parameter with the application-specific value of `header-example`.

The corresponding signature base is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@authority": example.com
"content-digest": sha-512=:WZDPaVn/7XgHaAy8pmojAkGWoRx2UFChF41A2svX\
  +TaPm+AbwAgBWnrIiYllu7BNNyealdVLvRwEmTHWXvJwew==:
"@query-param";name="Pet": dog
"@signature-params": ("@authority" "content-digest" \
  "@query-param";name="Pet")\
  ;created=1618884473;keyid="test-key-rsa-pss"\
  ;tag="header-example"
~~~


This results in the following Signature-Input and Signature header fields being added to the message under the label `sig-b22`:


~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b22=("@authority" "content-digest" \
  "@query-param";name="Pet");created=1618884473\
  ;keyid="test-key-rsa-pss";tag="header-example"
Signature: sig-b22=:LjbtqUbfmvjj5C5kr1Ugj4PmLYvx9wVjZvD9GsTT4F7GrcQ\
  EdJzgI9qHxICagShLRiLMlAJjtq6N4CDfKtjvuJyE5qH7KT8UCMkSowOB4+ECxCmT\
  8rtAmj/0PIXxi0A0nxKyB09RNrCQibbUjsLS/2YyFYXEu4TRJQzRw1rLEuEfY17SA\
  RYhpTlaqwZVtR8NV7+4UKkjqpcAoFqWFQh62s7Cl+H2fjBSpqfZUJcsIk4N6wiKYd\
  4je2U/lankenQ99PZfB4jY3I5rSV2DSBVkSFsURIjYErOs0tFTQosMTAoxk//0RoK\
  UqiYY8Bh0aaUEb0rQl3/XaVe4bXTugEjHSw==:
~~~

Note that the RSA PSS algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

### Full Coverage using rsa-pss-sha512

This example covers all applicable message components in `test-request` (including the content type and length) plus many derived components, again using the `rsa-pss-sha512` algorithm. Note that the `Host` header field is not covered because the `@authority` derived component is included instead.

The corresponding signature base is:

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

This results in the following Signature-Input and Signature header fields being added to the message under the label `sig-b23`:

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

The corresponding signature base is:

~~~
NOTE: '\' line wrapping per RFC 8792

"@status": 200
"content-type": application/json
"content-digest": sha-512=:mEWXIS7MaLRuGgxOBdODa3xqM1XdEvxoYhvlCFJ4\
  1QJgJc4GTsPp29l5oGX69wWdXymyU0rjJuahq4l5aGgfLQ==:
"content-length": 23
"@signature-params": ("@status" "content-type" "content-digest" \
  "content-length");created=1618884473;keyid="test-key-ecc-p256"
~~~

This results in the following Signature-Input and Signature header fields being added to the message under the label `sig-b24`:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b24=("@status" "content-type" \
  "content-digest" "content-length");created=1618884473\
  ;keyid="test-key-ecc-p256"
Signature: sig-b24=:wNmSUAhwb5LxtOtOpNa6W5xj067m5hFrj0XQ4fvpaCLx0NK\
  ocgPquLgyahnzDnDAUy5eCdlYUEkLIj+32oiasw==:
~~~

Note that the ECDSA algorithm in use here is non-deterministic, meaning a different signature value will be created every time the algorithm is run. The signature value provided here can be validated against the given keys, but newly-generated signature values are not expected to match the example. See {{security-nondeterministic}}.

### Signing a Request using hmac-sha256

This example covers portions of the `test-request` using the `hmac-sha256` algorithm and the
secret `test-shared-secret`.

The corresponding signature base is:

~~~
NOTE: '\' line wrapping per RFC 8792

"date": Tue, 20 Apr 2021 02:07:55 GMT
"@authority": example.com
"content-type": application/json
"@signature-params": ("date" "@authority" "content-type")\
  ;created=1618884473;keyid="test-shared-secret"
~~~

This results in the following Signature-Input and Signature header fields being added to the message under the label `sig-b25`:

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

The corresponding signature base is:

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

This results in the following Signature-Input and Signature header fields being added to the message under the label `sig-b26`:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig-b26=("date" "@method" "@path" "@authority" \
  "content-type" "content-length");created=1618884473\
  ;keyid="test-key-ed25519"
Signature: sig-b26=:wqcAqbmYJ2ji2glfAMaRy4gruYYnx2nEFN2HN6jrnDnQCK1\
  u02Gb04v9EDgwUPiu4A0w6vuQv5lIp5WPpBKRCw==:
~~~

## TLS-Terminating Proxies

In this example, there is a TLS-terminating reverse proxy sitting in front of the resource. The client does not sign the request but instead uses mutual TLS to make its call. The terminating proxy validates the TLS stream and injects a `Client-Cert` header according to {{CLIENT-CERT}}, and then applies a signature to this field. By signing this header field, a reverse proxy can not only attest to its own validation of the initial request's TLS parameters but also authenticate itself to the backend system independently of the client's actions.

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

Without a signature, the internal service would need to trust that the incoming connection has the right information. By signing the `Client-Cert` header and other portions of the internal request, the internal service can be assured that the correct party, the trusted proxy, has processed the request and presented it to the correct service. The proxy's signature base consists of the following:

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

## HTTP Message Transformations {#example-transform}

The HTTP protocol allows intermediaries and applications to transform an HTTP message without affecting the semantics of the message itself. HTTP message signatures are designed to be robust against many of these transformations in different circumstances.

For example, the following HTTP request message has been signed using the `ed25519` algorithm
and the key `test-key-ed25519`.

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

GET /demo?name1=Value1&Name2=value2 HTTP/1.1
Host: example.org
Date: Fri, 15 Jul 2022 14:24:55 GMT
Accept: application/json
Accept: */*
Signature-Input: transform=("@method" "@path" "@authority" \
  "accept");created=1618884473;keyid="test-key-ed25519"
Signature: transform=:ZT1kooQsEHpZ0I1IjCqtQppOmIqlJPeo7DHR3SoMn0s5J\
  Z1eRGS0A+vyYP9t/LXlh5QMFFQ6cpLt2m0pmj3NDA==:
~~~

The signature base string for this message is:

~~~
"@method": GET
"@path": /demo
"@authority": example.org
"accept": application/json, */*
"@signature-params": ("@method" "@path" "@authority" "accept")\
  ;created=1618884473;keyid="test-key-ed25519"
~~~

The following message has been altered by adding the Accept-Language header as well as adding a query parameter. However, since neither the Accept-Language header nor the query are covered by the signature, the same signature is still valid:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

GET /demo?name1=Value1&Name2=value2&param=added HTTP/1.1
Host: example.org
Date: Fri, 15 Jul 2022 14:24:55 GMT
Accept: application/json
Accept: */*
Accept-Language: en-US,en;q=0.5
Signature-Input: transform=("@method" "@path" "@authority" \
  "accept");created=1618884473;keyid="test-key-ed25519"
Signature: transform=:ZT1kooQsEHpZ0I1IjCqtQppOmIqlJPeo7DHR3SoMn0s5J\
  Z1eRGS0A+vyYP9t/LXlh5QMFFQ6cpLt2m0pmj3NDA==:
~~~

The following message has been altered by removing the Date header, adding a Referer header, and collapsing the Accept header into a single line. The Date and Referrer headers are not covered by the signature, and the collapsing of the Accept header is an allowed transformation that is already accounted for by the canonicalization algorithm for HTTP field values. The same signature is still valid:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

GET /demo?name1=Value1&Name2=value2 HTTP/1.1
Host: example.org
Referer: https://developer.example.org/demo
Accept: application/json, */*
Signature-Input: transform=("@method" "@path" "@authority" \
  "accept");created=1618884473;keyid="test-key-ed25519"
Signature: transform=:ZT1kooQsEHpZ0I1IjCqtQppOmIqlJPeo7DHR3SoMn0s5J\
  Z1eRGS0A+vyYP9t/LXlh5QMFFQ6cpLt2m0pmj3NDA==:
~~~

The following message has been altered by re-ordering the field values of the original message, but not re-ordering the individual Accept headers. The same signature is still valid:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

GET /demo?name1=Value1&Name2=value2 HTTP/1.1
Accept: application/json
Accept: */*
Date: Fri, 15 Jul 2022 14:24:55 GMT
Host: example.org
Signature-Input: transform=("@method" "@path" "@authority" \
  "accept");created=1618884473;keyid="test-key-ed25519"
Signature: transform=:ZT1kooQsEHpZ0I1IjCqtQppOmIqlJPeo7DHR3SoMn0s5J\
  Z1eRGS0A+vyYP9t/LXlh5QMFFQ6cpLt2m0pmj3NDA==:
~~~

The following message has been altered by changing the method to POST and the authority to "example.com" (inside the Host header). Since both the method and authority are covered by the signature, the same signature is NOT still valid:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

POST /demo?name1=Value1&Name2=value2 HTTP/1.1
Host: example.com
Date: Fri, 15 Jul 2022 14:24:55 GMT
Accept: application/json
Accept: */*
Signature-Input: transform=("@method" "@path" "@authority" \
  "accept");created=1618884473;keyid="test-key-ed25519"
Signature: transform=:ZT1kooQsEHpZ0I1IjCqtQppOmIqlJPeo7DHR3SoMn0s5J\
  Z1eRGS0A+vyYP9t/LXlh5QMFFQ6cpLt2m0pmj3NDA==:
~~~

The following message has been altered by changing the order of the two instances of the Accept header. Since the order of fields with the same name is semantically significant in HTTP, this changes the value used in the signature base, and the same signature is NOT still valid:

~~~ http-message
NOTE: '\' line wrapping per RFC 8792

GET /demo?name1=Value1&Name2=value2 HTTP/1.1
Host: example.org
Date: Fri, 15 Jul 2022 14:24:55 GMT
Accept: */*
Accept: application/json
Signature-Input: transform=("@method" "@path" "@authority" \
  "accept");created=1618884473;keyid="test-key-ed25519"
Signature: transform=:ZT1kooQsEHpZ0I1IjCqtQppOmIqlJPeo7DHR3SoMn0s5J\
  Z1eRGS0A+vyYP9t/LXlh5QMFFQ6cpLt2m0pmj3NDA==:
~~~

# Acknowledgements {#acknowledgements}
{:numbered="false"}

This specification was initially based on the draft-cavage-http-signatures internet draft. The editors would like to thank the authors of that draft, Mark Cavage and Manu Sporny, for their work on that draft and their continuing contributions. The specification also includes contributions from the draft-oauth-signed-http-request internet draft and other similar efforts.

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
Tyler Ham,
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

  - -16
     *

  - -15
     * Editorial cleanup.
     * Defined "signature context".

  - -14
     * Target raw non-decoded values for "@query" and "@path".
     * Add method for signing trailers.
     * Call out potential issues of list-based field values.
     * Update IANA registry for header fields.
     * Call out potential issues with Content-Digest in example.
     * Add JWK formats for all keys.

  - -13
     * Renamed "context" parameter to "tag".
     * Added discussion on messages with multiple known contexts.

  - -12
     * Added "context" parameter.
     * Added set of safe transformation examples.
     * Added ECDSA over P-384.
     * Expanded definiton of message component source context.
     * Sorted security considerations into categories.

  - -11
     * Added ABNF references, coalesced ABNF rules.
     * Editorial and formatting fixes.
     * Update examples.
     * Added Byte Sequence field value wrapping.

  - -10
     * Removed "related response" and "@request-response" in favor of generic "req" parameter.
     * Editorial fixes to comply with HTTP extension style guidelines.
     * Add security consideration on message content.

  - -09
     * Explained key formats better.
     * Removed "host" and "date" from most examples.
     * Fixed query component  generation.
     * Renamed "signature input" and "signature input string" to "signature base".
     * Added consideration for semantically equivalent field values.

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
