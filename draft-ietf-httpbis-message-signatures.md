---
title: Signing HTTP Messages
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
    FIPS186-4:
        target: https://csrc.nist.gov/publications/detail/fips/186/4/final
        title: Digital Signature Standard (DSS)
        date: 2013
    POSIX.1:
        target: https://pubs.opengroup.org/onlinepubs/9699919799/
        title: The Open Group Base Specifications Issue 7, 2018 edition
        date: 2018

informative:
    RFC6234:
    RFC7517:
    RFC7518:
    RFC7239:
    RFC8017:
    WP-HTTP-Sig-Audit:
        target: https://web-payments.org/specs/source/http-signatures-audit/
        title: Security Considerations for HTTP Signatures
        date: 2013

--- abstract

This document describes a mechanism for creating, encoding, and verifying digital signatures or message authentication codes over content within an HTTP message.  This mechanism supports use cases where the full HTTP message may not be known to the signer, and where the message may be transformed (e.g., by intermediaries) before reaching the verifier.

--- note_Note_to_Readers

*RFC EDITOR: please remove this section before publication*

Discussion of this draft takes place on the HTTP working group mailing list (ietf-http-wg@w3.org), which is archived at <https://lists.w3.org/Archives/Public/ietf-http-wg/>.

Working Group information can be found at <https://httpwg.org/>; source code and issues list for this draft can be found at <https://github.com/httpwg/http-extensions/labels/signatures>.

--- middle

# Introduction {#intro}

Message integrity and authenticity are important security properties that are critical to the secure operation of many HTTP applications.
Application developers typically rely on the transport layer to provide these properties, by operating their application over {{?TLS=RFC8446}}.  However, TLS only guarantees these properties over a single TLS connection, and the path between client and application may be composed of multiple independent TLS connections (for example, if the application is hosted behind a TLS-terminating gateway or if the client is behind a TLS Inspection appliance).  In such cases, TLS cannot guarantee end-to-end message integrity or authenticity between the client and application.  Additionally, some operating environments present obstacles that make it impractical to use TLS, or to use features necessary to provide message authenticity.  Furthermore, some applications require the binding of an application-level key to the HTTP message, separate from any TLS certificates in use. Consequently, while TLS can meet message integrity and authenticity needs for many HTTP-based applications, it is not a universal solution.

This document defines a mechanism for providing end-to-end integrity and authenticity for content within an HTTP message.  The mechanism allows applications to create digital signatures or message authentication codes (MACs) over only that content within the message that is meaningful and appropriate for the application.  Strict canonicalization rules ensure that the verifier can verify the signature even if the message has been transformed in any of the many ways permitted by HTTP.

The mechanism described in this document consists of three parts:

- A common nomenclature and canonicalization rule set for the different protocol elements and other content within HTTP messages.
- Algorithms for generating and verifying signatures over HTTP message content using this nomenclature and rule set.
- A mechanism for attaching a signature and related metadata to an HTTP message.

## Requirements Discussion

HTTP permits and sometimes requires intermediaries to transform messages in a variety of ways.  This may result in a recipient receiving a message that is not bitwise equivalent to the message that was originally sent.  In such a case, the recipient will be unable to verify a signature over the raw bytes of the sender's HTTP message, as verifying digital signatures or MACs requires both signer and verifier to have the exact same signed content.  Since the raw bytes of the message cannot be relied upon as signed content, the signer and verifier must derive the signed content from their respective versions of the message, via a mechanism that is resilient to safe changes that do not alter the meaning of the message.

For a variety of reasons, it is impractical to strictly define what constitutes a safe change versus an unsafe one.  Applications use HTTP in a wide variety of ways, and may disagree on whether a particular piece of information in a message (e.g., the body, or the `Date` header field) is relevant.  Thus a general purpose solution must provide signers with some degree of control over which message content is signed.

HTTP applications may be running in environments that do not provide complete access to or control over HTTP messages (such as a web browser's JavaScript environment), or may be using libraries that abstract away the details of the protocol (such as [the Java HTTPClient library](https://openjdk.java.net/groups/net/httpclient/intro.html)).  These applications need to be able to generate and verify signatures despite incomplete knowledge of the HTTP message.

## HTTP Message Transformations {#transforms}

As mentioned earlier, HTTP explicitly permits and in some cases requires implementations to transform messages in a variety of ways.  Implementations are required to tolerate many of these transformations.  What follows is a non-normative and non-exhaustive list of transformations that may occur under HTTP, provided as context:

- Re-ordering of header fields with different header field names ({{MESSAGING}}, Section 3.2.2).
- Combination of header fields with the same field name ({{MESSAGING}}, Section 3.2.2).
- Removal of header fields listed in the `Connection` header field ({{MESSAGING}}, Section 6.1).
- Addition of header fields that indicate control options ({{MESSAGING}}, Section 6.1).
- Addition or removal of a transfer coding ({{MESSAGING}}, Section 5.7.2).
- Addition of header fields such as `Via` ({{MESSAGING}}, Section 5.7.1) and `Forwarded` ([RFC7239], Section 4).

## Safe Transformations

Based on the definition of HTTP and the requirements described above, we can identify certain types of transformations that should not prevent signature verification, even when performed on content covered by the signature.  The following list describes those transformations:

- Combination of header fields with the same field name.
- Reordering of header fields with different names.
- Conversion between different versions of the HTTP protocol (e.g., HTTP/1.x to HTTP/2, or vice-versa).
- Changes in casing (e.g., "Origin" to "origin") of any case-insensitive content such as header field names, request URI scheme, or host.
- Addition or removal of leading or trailing whitespace to a header field value.
- Addition or removal of `obs-folds`.
- Changes to the `request-target` and `Host` header field that when applied together do not
  result in a change to the message's effective request URI, as defined in Section 5.5 of
  {{MESSAGING}}.

Additionally, all changes to content not covered by the signature are considered safe.


## Conventions and Terminology {#definitions}

{::boilerplate bcp14}

The terms "HTTP message", "HTTP request", "HTTP response",
`absolute-form`, `absolute-path`, "effective request URI",
"gateway", "header field", "intermediary", `request-target`,
"sender", and "recipient" are used as defined in {{!MESSAGING=RFC7230}}.

The term "method" is to be interpreted as defined in Section 4 of {{!SEMANTICS=RFC7231}}.

For brevity, the term "signature" on its own is used in this document to refer to both digital signatures and keyed MACs.  Similarly, the verb "sign" refers to the generation of either a digital signature or keyed MAC over a given input string.  The qualified term "digital signature" refers specifically to the output of an asymmetric cryptographic signing operation.

In addition to those listed above, this document uses the following terms:

{: vspace="0"}
Signer:
: The entity that is generating or has generated an HTTP Message Signature.

Verifier:
: An entity that is verifying or has verified an HTTP Message Signature against an HTTP Message.  Note that an HTTP Message Signature may be verified multiple times, potentially by different entities.

Covered Content:
: An ordered list of content identifiers for headers ({{http-header}}) and specialty content ({{specialty-content}}) that indicates the metadata and message content that is covered by the signature, not including the `@signature-params` specialty field itself.

HTTP Signature Algorithm:
: A cryptographic algorithm that describes the signing and verification process for the signature. When expressed explicitly, the value maps to a string defined in the HTTP Signature Algorithms Registry defined in this document.

Key Material:
: The key material required to create or verify the signature. The key material is often identified with an explicit key identifier, allowing the signer to indicate to the verifier which key was used.

Creation Time:
: A timestamp representing the point in time that the signature was generated, as asserted by the signer.

Expiration Time:
: A timestamp representing the point in time at which the signature expires, as asserted by the signer. A signature's expiration time could be undefined, indicating that the signature does not expire from the perspective of the signer.

The term "Unix time" is defined by {{POSIX.1}}, [Section 4.16](http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html#tag_04_16).

This document contains non-normative examples of partial and complete HTTP messages. Some examples use a single trailing backslash '\' to indicate line wrapping for long values, as per {{!RFC8792}}. The `\` character and leading spaces on wrapped lines are not part of the value.

## Application of HTTP Message Signatures {#application}

HTTP Message Signatures are designed to be a general-purpose security mechanism applicable in a wide variety of circumstances and applications. In order to properly and safely apply HTTP Message Signatures, an application or profile of this specification MUST specify all of the following items:

- The set of [content identifiers](#covered-content) that are expected and required. For example, an authorization protocol could mandate that the `Authorization` header be covered to protect the authorization credentials and mandate the signature parameters contain a `created` parameter, while an API expecting HTTP message bodies could require the `Digest` header to be present and covered.
- A means of retrieving the key material used to verify the signature. An application will usually use the `keyid` parameter of the signature parameters ({{signature-params}}) and define rules for resolving a key from there, though the appropriate key could be known from other means.
- A means of determining the signature algorithm used to verify the signature content is appropriate for the key material. For example, the process could use the `alg` parameter of the signature parameters ({{signature-params}}) to state the algorithm explicitly, derive the algorithm from the key material, or use some pre-configured algorithm agreed upon by the signer and verifier.
- A means of determining that a given key and algorithm presented in the request are appropriate for the request being made. For example, a server expecting only ECDSA signatures should know to reject any RSA signatures, or a server expecting asymmetric cryptography should know to reject any symmetric cryptography.

The details of this kind of profiling are the purview of the application and outside the scope of this specification.

# HTTP Message Signature Covered Content {#covered-content}

In order to allow signers and verifiers to establish which content is covered by a signature, this document defines content identifiers for data items covered by an HTTP Message Signature as well as the means for combining these canonicalized values into a signature input string.

Some content within HTTP messages can undergo transformations that change the bitwise value without altering meaning of the content (for example, the merging together of header fields with the same name).  Message content must therefore be canonicalized before it is signed, to ensure that a signature can be verified despite such intermediary transformations. This document defines rules for each content identifier that transform the identifier's associated content into such a canonical form.

Content identifiers are defined using production grammar defined by [RFC8941, Section 4](#RFC8941).
The content identifier is an `sf-string` value. The content identifier
type MAY define parameters which are included using the `parameters` rule.

~~~ abnf
content-identifier = sf-string parameters
~~~

Note that this means the value of the identifier itself is encased in double quotes, with parameters following as a semicolon-separated list, such as `"cache-control"`, `"date"`, or `"@signature-params"`.

The following sections define content identifier types, their parameters, their associated content, and their canonicalization rules. The method for combining content identifiers into the signature input string is defined in {{create-sig-input}}.

## HTTP Headers {#http-header}

The content identifier for an HTTP header is the lowercased form of its header field name. While HTTP header field names are case-insensitive, implementations MUST use lowercased field names (e.g., `content-type`, `date`, `etag`) when using them as content identifiers.

Unless overridden by additional parameters and rules, the HTTP header field value MUST be canonicalized with the following steps:

1. Create an ordered list of the field values of each instance of the header field in the message, in the order that they occur (or will occur) in the message.
2. Strip leading and trailing whitespace from each item in the list.
3. Concatenate the list items together, with a comma "," and space " " between each item. 

The resulting string is the canonicalized value.

### Canonicalized Structured HTTP Headers {#http-header-structured}

If value of the the HTTP header in question is a structured field ({{!RFC8941}}), the content identifier MAY include the `sf` parameter. If this
parameter is included, the HTTP header value MUST be canonicalized using the rules specified in [Section 4 of RFC8941](#RFC8941). Note that this process
will replace any optional whitespace with a single space.

The resulting string is used as the field value input in {{http-header}}.

### Canonicalization Examples

This section contains non-normative examples of canonicalized values for header fields, given the following example HTTP message:

~~~ http-message
Server: www.example.com
Date: Tue, 07 Jun 2014 20:51:35 GMT
X-OWS-Header:   Leading and trailing whitespace.    
X-Obs-Fold-Header: Obsolete
    line folding.
X-Empty-Header:
Cache-Control: max-age=60
Cache-Control:    must-revalidate
~~~

The following table shows example canonicalized values for header fields, given that message:

|Header Field|Canonicalized Value|
|--- |--- |
|`"cache-control"`|max-age=60, must-revalidate|
|`"date"`|Tue, 07 Jun 2014 20:51:35 GMT|
|`"server"`|www.example.com|
|`"x-empty-header"`||
|`"x-obs-fold-header"`|Obsolete line folding.|
|`"x-ows-header"`|Leading and trailing whitespace.|
{: title="Non-normative examples of header field canonicalization."}

## Dictionary Structured Field Members

An individual member in the value of a Dictionary Structured Field is identified by using the parameter `key` on the content identifier for the header. The value of this parameter is a the key being identified, without any parameters present on that key in the original dictionary.

An individual member in the value of a Dictionary Structured Field is canonicalized by applying the serialization algorithm described in [Section 4.1.2 of RFC8941](#RFC8941) on a Dictionary containing only that member.

### Canonicalization Examples

This section contains non-normative examples of canonicalized values for Dictionary Structured Field Members given the following example header field, whose value is assumed to be a Dictionary:

~~~ http-message
X-Dictionary:  a=1, b=2;x=1;y=2, c=(a b c)
~~~

The following table shows example canonicalized values for different content identifiers, given that field:

|Content Identifier|Canonicalized Value|
|--- |--- |
|`"x-dictionary";key=a`|1|
|`"x-dictionary";key=b`|2;x=1;y=2|
|`"x-dictionary";key=c`|(a, b, c)|
{: title="Non-normative examples of Dictionary member canonicalization."}


## List Prefixes

A prefix of a List Structured Field consisting of the first N members in the field's value (where N is an integer greater than 0 and less than or equal to the number of members in the List) is identified by the parameter `prefix` with the value of N as an integer. 

A list prefix value is canonicalized by applying the serialization algorithm described in [Section 4.1.1 of RFC8941](#RFC8941) on a List containing only the first N members as specified in the list prefix, in the order they appear in the original List.

### Canonicalization Examples

This section contains non-normative examples of canonicalized values for list prefixes given the following example header fields, whose values are assumed to be Dictionaries:

~~~ http-message
X-List-A: (a b c d e f)
X-List-B: ()
~~~

The following table shows example canonicalized values for different content identifiers, given those fields:

|Content Identifier|Canonicalized Value|
|--- |--- |
|`"x-list-a";prefix=0`|()|
|`"x-list-a";prefix=1`|(a)|
|`"x-list-a";prefix=3`|(a, b, c)|
|`"x-list-a";prefix=6`|(a, b, c, d, e, f)|
|`"x-list-b";prefix=0`|()|
{: title="Non-normative examples of list prefix canonicalization."}


## Specialty Content Fields {#specialty-content}

Content not found in an HTTP header can be included in the signature base string by defining a content identifier and the canonicalization method for its content.

To differentiate specialty content identifiers from HTTP headers, specialty content identifiers MUST start with the "at" `@` character. This specification defines the following specialty content identifiers:

@request-target
: The target request endpoint. ({{content-request-target}})

@signature-params
: The signature metadata parameters for this signature. ({{signature-params}})

Additional specialty content identifiers MAY be defined and registered in the HTTP Signatures Specialty Content Identifier Registry. ({{content-registry}})

### Request Target {#content-request-target}

The request target endpoint, consisting of the request method and the path and query of the effective request URI, is identified by the `@request-target` identifier.

Its value is canonicalized as follows:

1. Take the lowercased HTTP method of the message.
2. Append a space " ".
3. Append the path and query of the request target of the message, formatted according to the rules defined for the :path pseudo-header in {{!HTTP2=RFC7540}}, Section 8.1.2.3.  The resulting string is the canonicalized value.

#### Canonicalization Examples

The following table contains non-normative example HTTP messages and their canonicalized `@request-target` values.

<table>
    <name>Non-normative examples of <tt>@request-target</tt> canonicalization.</name>
    <thead>
        <tr><th>HTTP Message</th><th>@request-target</th></tr>
    </thead>
    <tbody>
        <tr>
            <td><sourcecode type="http-message">
POST /?param=value HTTP/1.1
Host: www.example.com</sourcecode></td>
            <td><tt>post /?param=value</tt></td>
        </tr>
        <tr>
            <td><sourcecode type="http-message">
POST /a/b HTTP/1.1
Host: www.example.com</sourcecode></td>
            <td><tt>post /a/b</tt></td>
        </tr>
        <tr>
            <td><sourcecode type="http-message">
GET http://www.example.com/a/ HTTP/1.1</sourcecode></td>
            <td><tt>get /a/</tt></td>
        </tr>
        <tr>
            <td><sourcecode type="http-message">
GET http://www.example.com HTTP/1.1</sourcecode></td>
            <td><tt>get /</tt></td>
        </tr>
        <tr>
            <td><sourcecode type="http-message">
CONNECT server.example.com:80 HTTP/1.1
Host: server.example.com</sourcecode></td>
            <td><tt>connect /</tt></td>
        </tr>
        <tr>
            <td><sourcecode type="http-message">
OPTIONS * HTTP/1.1
Host: server.example.com</sourcecode></td>
            <td><tt>options *</tt></td>
        </tr>
    </tbody>
</table>

### Signature Parameters {#signature-params}

HTTP Message Signatures have metadata properties that provide information regarding the signature's generation and/or verification.

The signature parameters special content is identified by the `@signature-params` identifier.

Its canonicalized value is the serialization of the signature parameters for this signature, including the covered content list with all associated parameters. The following metadata properties are defined:

The signature parameters are serialized using the rules in [Section 4 of RFC8941](#RFC8941) as follows:

1. Let the output be an empty string.
2. Determine an order for the content identifiers of the covered content. Once this order is chosen, it cannot be changed.
3. Serialize the content identifiers of the covered content as an ordered `inner-list` according to [Section 4.1.1.1 of RFC8941](#RFC8941) and append this to the output.
4. Determine an order for signature metadata parameters. Once this order is chosen, it cannot be changed.
5. Append the signature metadata as parameters according to [Section 4.1.1.2 of RFC8941](#RFC8941) in the chosen order,
    skipping fields that are not available or not used for this signature:
   * `alg`: The HTTP message signature algorithm from the HTTP Message Signature Algorithm Registry, as an `sf-string` value.
   * `keyid`: The identifier for the key material as an `sf-string` value.
   * `created`: Creation time as an `sf-integer` UNIX timestamp value. Sub-second precision is not supported.
   * `expires`: Expiration time as an `sf-integer` UNIX timestamp value. Sub-second precision is not supported.
   * `nonce`: A random unique value generated for this signature.
6. The output contains the signature parameters value.

Note that the `inner-list` serialization is used for the covered content value instead of the `sf-list` serialization 
in order to facilitate this value's additional inclusion in the `Signature-Input` header's dictionary, 
as discussed in {{signature-input-header}}.

This example shows a canonicalized value for the parameters of a given signature:

~~~
("@request-target" "host" "date" "cache-control" "x-empty-header" \
  "x-example");keyid="test-key-rsa-pss";alg="rsa-pss-sha512";\
  created=1618884475;expires=1618884775
~~~

Note that an HTTP message could contain multiple signatures, but only the signature parameters used for the current signature are included in this field.

## Creating the Signature Input String {#create-sig-input}

The signature input is a US-ASCII string containing the content that is covered by the signature. To create the signature input string, the signer or verifier concatenates together entries for each identifier in the signature's covered content and parameters using the following algorithm:

1. Let the output be an empty string.

2. For each covered content item in the covered content list (in order):

    1. Append the identifier for the covered content serialized according to the `content-identifier` rule.

    2. Append a single colon `":"`

    3. Append a single space `" "`

    4. Append the covered content's canonicalized value, as defined by the covered content type. ({{http-header}} and {{specialty-content}})

    5. Append a single newline `"\\n"`

3. Append the signature parameters ({{signature-params}}) as follows:

    1. Append the identifier for the signature parameters serialized according to the `content-identifier` rule, `"@signature-params"`

    2. Append a single colon `":"`

    3. Append a single space `" "`

    4. Append the signature parameters' canonicalized value as defined in {{signature-params}}

4. Return the output string.    

If covered content references an identifier that cannot be resolved to a value in the message, the implementation MUST produce an error. Such situations are included but not limited to:

 * The signer or verifier does not understand the content identifier.
 * The identifier identifies a header field that is not present in the message or whose value is malformed.
 * The identifier is a Dictionary member identifier that references a header field that is not present in the message, is not a Dictionary Structured Field, or whose value is malformed.
 * The identifier is a List Prefix member identifier that references a header field that is not present in the message, is not a List Structured Field, or whose value is malformed.
 * The identifier is a Dictionary member identifier that references a member that is not present in the header field value, or whose value is malformed. E.g., the identifier is `"x-dictionary";key=c` and the value of the `x-dictionary` header field is `a=1, b=2`
 * The identifier is a List Prefix member identifier that specifies more List members than are present the header field. E.g., the identifier is `"x-list";prefix=3` and the value of the `x-list` header field is `(1, 2)`.

In the following non-normative example, the HTTP message being signed is the following request:

~~~ http-message
GET /foo HTTP/1.1
Host: example.org
Date: Tue, 20 Apr 2021 02:07:55 GMT
X-Example: Example header
        with some whitespace.
X-Empty-Header:
Cache-Control: max-age=60
Cache-Control: must-revalidate
~~~

The covered content consists of the `@request-target` speciality header followed by the `Host`, `Date`, `Cache-Control`, `X-Empty-Header`, `X-Example` HTTP headers, in order. The signature creation timestamp is `1618884475` and the key identifier is `test-key-rsa-pss`.  The signature input string for this message with these parameters is:

~~~
"@request-target": get /foo
"host": example.org
"date": Tue, 20 Apr 2021 02:07:55 GMT
"cache-control": max-age=60, must-revalidate
"x-empty-header": 
"x-example": Example header with some whitespace.
"@signature-params": ("@request-target" "host" "date" "cache-control" \
  "x-empty-header" "x-example");created=1618884475;\
  keyid="test-key-rsa-pss"
~~~
{: title="Non-normative example Signature Input" artwork-name="example-sig-input" #example-sig-input}

# HTTP Message Signatures {#message-signatures}

An HTTP Message Signature is a signature over a string generated from a subset of the content in an HTTP message and metadata about the signature itself.  When successfully verified against an HTTP message, it provides cryptographic proof that with respect to the subset of content that was signed, the message is semantically equivalent to the message for which the signature was generated.

## Creating a Signature {#sign}

In order to create a signature, a signer MUST follow the following algorithm:

1. The signer chooses an HTTP signature algorithm and key material for signing. The signer MUST choose key material that is appropriate 
    for the signature's algorithm, and that conforms to any requirements defined by the algorithm, such as key size or format. The 
    mechanism by which the signer chooses the algorithm and key material is out of scope for this document.

2. The signer sets the signature's creation time to the current time.

3. If applicable, the signer sets the signature's expiration time property to the time at which the signature is to expire.

4. The signer creates an ordered list of content identifiers representing the message content and signature metadata to be covered by the signature, and assigns this list as the signature's Covered Content.
   * Once an order of covered content is chosen, the order MUST NOT change for the life of the signature.
   * Each covered content identifier MUST either reference an HTTP header in the request message {{http-header}} or reference a specialty content field listed in {{specialty-content}} or its associated registry.
   * Signers SHOULD include `@request-target` in the covered content list list.
   * Signers SHOULD include a date stamp in some form, such as using the `date` header. Alternatively, the `created` signature metadata parameter can fulfil this role.
   * Further guidance on what to include in this list and in what order is out of scope for this document. However, note that the list order is significant and once established for a given signature it MUST be preserved for that signature.
   * Note that the `@signature-params` specialty identifier is not explicitly listed in the list of covered content identifiers, because it is required to always be present as the last line in the signature input. This ensures that a signature always covers its own metadata.

5. The signer creates the signature input string. ({{create-sig-input}})

6. The signer signs the signature input with the chosen signing algorithm using the key material chosen by the signer. Several signing algorithms are defined in in {{signature-methods}}.

6. The byte array output of the signature function is the HTTP message signature output value to be included in the `Signature` header as defined in {{signature-header}}.

For example, given the HTTP message and signature parameters in the example in {{create-sig-input}}, the example signature input string when signed with the `test-key-rsa-pss` key in {{example-key-rsa-pss-test}} gives the following message signature output value, encoded in Base64:

~~~
:H00a6KdNCRWgOWBMvuRtxh6c/wrVxwt2p5KyqBJqmtPbNTd980hWwkUE6H4NWiTs5f2Ef0\
qJ3iypXT2bR9Pc+PVU9U2gAzTcZKK8MDJLjYKfaE835zg/9sOdGR+tlRJ1cbCoWMVoCgEPi\
4t6QewbI0xgdx8AmP5ItTunYmhe8G0JR42lfvz60+szb8SpwJEmkMPr5dBOz6DLEeM3IgKN\
oBlJPp94WSJkgvwTM64rXw049ZkYenl9jwKlcXEmA1a4MNWoUElr6eh5k20djMZftCYTPUU\
PMxZUavcQy+cp6lfKonz6HIDe3+n3VOTOo8uu1aSVfKQQzR+ZEwSaZQBrdQ==:
~~~
{: title="Non-normative example signature value" #example-sig-value}


## Verifying a Signature {#verify}

A verifier processes a signature and its associated signature input parameters in concert with each other.

In order to verify a signature, a verifier MUST follow the following algorithm:

1. Parse the `Signature` and `Signature-Input` headers and extract the signatures to be verified.
    1. If there is more than one signature value present, determine which signature should be processed
        for this request. If an appropriate signature is not found, produce an error.
    2. If the chosen `Signature` value does not have a corresponding `Signature-Input` value,
        produce an error.
2. Parse the values of the chosen `Signature-Input` header field to get the parameters for the
    signature to be verified.
3. Parse the value of the corresponding `Signature` header field to get the byte array value of the signature
    to be verified.
4. Examine the signature parameters to confirm that the signature meets the requirements described 
    in this document, as well as any additional requirements defined by the application such as which 
    contents are required to be covered by the signature. ({{verify-requirements}})
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
    the value of the SignatureInput header field for this signature serialized according to the rules described
    in {{signature-params}}, not including the signature's label from the `Signature-Input` header.
8. If the key material is appropriate for the algorithm, apply the verification algorithm to the signature,
    recalculated signature input, signature parameters, key material, and algorithm. Several algorithms are defined in
    {{signature-methods}}.
9. The results of the verification algorithm function are the final results of the signature verification. 

If any of the above steps fail, the signature validation fails. 


### Enforcing Application Requirements {#verify-requirements}

The verification requirements specified in this document are intended as a baseline set of restrictions that are generally applicable to all use cases.  Applications using HTTP Message Signatures MAY impose requirements above and beyond those specified by this document, as appropriate for their use case.

Some non-normative examples of additional requirements an application might define are:

- Requiring a specific set of header fields to be signed (e.g., Authorization, Digest).
- Enforcing a maximum signature age.
- Prohibiting the use of certain algorithms, or mandating the use of an algorithm.
- Requiring keys to be of a certain size (e.g., 2048 bits vs. 1024 bits).
- Enforcing uniqueness of a nonce value.

Application-specific requirements are expected and encouraged.  When an application defines additional requirements, it MUST enforce them during the signature verification process, and signature verification MUST fail if the signature does not conform to the application's requirements.

Applications MUST enforce the requirements defined in this document.  Regardless of use case, applications MUST NOT accept signatures that do not conform to these requirements.

## Signature Algorithm Methods {#signature-methods}

HTTP Message signatures MAY use any cryptographic digital signature or MAC method that is appropriate for the key material,
environment, and needs of the signer and verifier.
All signatures are generated from and verified against the byte values of the signature input string defined in {{create-sig-input}}.

Each signature algorithm method takes as its input the signature input string as a set of byte values (`I`), the signing key material
(`Ks`), and outputs the signed content as a set of byte values (`S`):

~~~
HTTP_SIGN (I, Ks)  ->  S
~~~

Each verification algorithm method takes as its input the recalculated signature input string as a set of byte values (`I`), the verification key
material (`Kv`), and the presented signature to be verified as a set of byte values (`S`) and outputs the verification result (`V`) as a boolean:

~~~
HTTP_VERIFY (I, Kv, S) -> V
~~~

This section contains several common algorithm methods. The method to use can be communicated through the algorithm signature parameter
defined in {{signature-params}}, by reference to the key material, or through mutual agreement between the signer and verifier.

### RSASSA-PSS using SHA-512 {#method-rsa-pss-sha512}

To sign using this algorithm, the signer applies the `RSASSA-PSS-SIGN (K, M)` function {{RFC8017}} with the signer's private signing key (`K`) and
the signature input string (`M`) ({{create-sig-input}}). 
The hash SHA-512 {{RFC6234}} is applied to the signature input string to create
the digest content to which the digital signature is applied. 
The resulting signed content byte array (`S`) is the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `RSASSA-PSS-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key portion of the verification key material (`(n, e)`) and the signature input string (`M`) re-created as described in {{verify}}.
The hash function SHA-512 {{RFC6234}} is applied to the signature input string to create the digest content to which the verification function is applied. 
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The results of the verification function are compared to the http message signature to determine if the signature presented is valid.

### RSASSA-PKCS1-v1_5 using SHA-256 {#method-rsa-v1_5-sha256}

To sign using this algorithm, the signer applies the `RSASSA-PKCS1-V1_5-SIGN (K, M)` function {{RFC8017}} with the signer's private signing key (`K`) and
the signature input string (`M`) ({{create-sig-input}}). 
The hash SHA-256 {{RFC6234}} is applied to the signature input string to create
the digest content to which the digital signature is applied. 
The resulting signed content byte array (`S`) is the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `RSASSA-PSS-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key portion of the verification key material (`(n, e)`) and the signature input string (`M`) re-created as described in {{verify}}.
The hash function SHA-256 {{RFC6234}} is applied to the signature input string to create the digest content to which the verification function is applied. 
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The results of the verification function are compared to the http message signature to determine if the signature presented is valid.

### HMAC using SHA-256 {#method-hmac-sha256}

To sign and verify using this algorithm, the signer applies the `HMAC` function {{RFC2104}} with the shared signing key (`K`) and
the signature input string (`text`) ({{create-sig-input}}). 
The hash function SHA-256 {{RFC6234}} is applied to the signature input string to create the digest content to which the HMAC is applied, giving the signature result. 

For signing, the resulting value is the HTTP message signature output used in {{sign}}.

For verification, the verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The output of the HMAC function is compared to the value of the HTTP message signature, and the results of the comparison determine the validity of the signature presented.

### ECDSA using curve P-256 DSS and SHA-256 {#method-ecdsa-p256-sha256}

To sign using this algorithm, the signer applies the `ECDSA` algorithm {{FIPS186-4}} using curve P-256 with the signer's private signing key and
the signature input string ({{create-sig-input}}). 
The hash SHA-256 {{RFC6234}} is applied to the signature input string to create
the digest content to which the digital signature is applied. 
The resulting signed content byte array is the HTTP message signature output used in {{sign}}.

To verify using this algorithm, the verifier applies the `ECDSA` algorithm {{FIPS186-4}}  using the public key portion of the verification key material and the signature input string re-created as described in {{verify}}.
The hash function SHA-256 {{RFC6234}} is applied to the signature input string to create the digest content to which the verification function is applied. 
The verifier extracts the HTTP message signature to be verified (`S`) as described in {{verify}}.
The results of the verification function are compared to the http message signature to determine if the signature presented is valid.

### JSON Web Signature (JWS) algorithms {#method-jose}

If the signing algorithm is a JOSE signing algorithm from the JSON Web Signature and Encryption Algorithms Registry established by {{RFC7518}}, the 
JWS algorithm definition determines the signature and hashing algorithms to apply for both signing and verification. There is no
use of the explicit `alg` signature parameter when using JOSE signing algorithms.

For both signing and verification, the HTTP messages signature input string ({{create-sig-input}}) is used as the entire "JWS Signing Input". 
The JOSE Header defined in {{RFC7517}} is not used, and the signature input string is not first encoded in Base64 before applying the algorithm. 
The output of the JWS signature is taken as a byte array prior to the Base64url encoding used in JOSE.

The JWS algorithm MUST NOT be `none` and MUST NOT be any algorithm with a JOSE Implementation Requirement of `Prohibited`.

# Including a Message Signature in a Message
Message signatures can be included within an HTTP message via the `Signature-Input` and `Signature` HTTP header fields, both defined within this specification. 

An HTTP message signature MUST use both headers:
the `Signature` HTTP header field contains the signature value, while the `Signature-Input` HTTP header field identifies the covered content and parameters that describe how the signature was generated. Each header MAY contain multiple labeled values, where the labels determine the correlation between the `Signature` and `Signature-Input` fields. 

## The 'Signature-Input' HTTP Header {#signature-input-header}
The `Signature-Input` HTTP header field is a Dictionary Structured Header {{!RFC8941}} containing the metadata for one or more message signatures generated from content within the HTTP message. Each member describes a single message signature. The member's name is an identifier that uniquely identifies the message signature within the context of the HTTP message. The member's value is the serialization of the covered content including all signature metadata parameters, using the serialization process defined in {{signature-params}}.

~~~
Signature-Input: sig1=("@request-target" "host" "date" "cache-control" \
  "x-empty-header" "x-example");created=1618884475;\
  keyid="test-key-rsa-pss"
~~~

To facilitate signature validation, the `Signature-Input` header value MUST contain the same serialized value used 
in generating the signature input string's `@signature-params` value.

## The 'Signature' HTTP Header {#signature-header}
The `Signature` HTTP header field is a Dictionary Structured Header {{!RFC8941}} containing one or more message signatures generated from content within the HTTP message. Each member's name is a signature identifier that is present as a member name in the `Signature-Input` Structured Header within the HTTP message. Each member's value is a Byte Sequence containing the signature value for the message signature identified by the member name. Any member in the `Signature` HTTP header field that does not have a corresponding member in the HTTP message's `Signature-Input` HTTP header field MUST be ignored.

~~~
Signature: sig1=:H00a6KdNCRWgOWBMvuRtxh6c/wrVxwt2p5KyqBJqmtPbNTd980hWwk\
  UE6H4NWiTs5f2Ef0qJ3iypXT2bR9Pc+PVU9U2gAzTcZKK8MDJLjYKfaE835zg/9sOdGR+\
  tlRJ1cbCoWMVoCgEPi4t6QewbI0xgdx8AmP5ItTunYmhe8G0JR42lfvz60+szb8SpwJEm\
  kMPr5dBOz6DLEeM3IgKNoBlJPp94WSJkgvwTM64rXw049ZkYenl9jwKlcXEmA1a4MNWoU\
  Elr6eh5k20djMZftCYTPUUPMxZUavcQy+cp6lfKonz6HIDe3+n3VOTOo8uu1aSVfKQQzR\
  +ZEwSaZQBrdQ==:
~~~

## Multiple Signatures

Since `Signature-Input` and `Signature` are both defined as Dictionary Structured Headers, they can be used to include multiple signatures within the same HTTP message. For example, a signer may include multiple signatures signing the same content with different keys or algorithms to support verifiers with different capabilities, or a reverse proxy may include information about the client in header fields when forwarding the request to a service host, including a signature over those fields and the client's original signature. 

The following is a non-normative example of header fields a reverse proxy in addition to the examples in the previous sections. The original signature is included under the identifier `sig1`, and the reverse proxy's signature is included under `proxy_sig`. The proxy uses the key `rsa-test-key` to create its signature using the `rsa-v1_5-sha256` signature value. This results in a signature input string of:

~~~
"signature";key="sig1": :H00a6KdNCRWgOWBMvuRtxh6c/wrVxwt2p5KyqBJqmtPbNT\
  d980hWwkUE6H4NWiTs5f2Ef0qJ3iypXT2bR9Pc+PVU9U2gAzTcZKK8MDJLjYKfaE835zg\
  /9sOdGR+tlRJ1cbCoWMVoCgEPi4t6QewbI0xgdx8AmP5ItTunYmhe8G0JR42lfvz60+sz\
  b8SpwJEmkMPr5dBOz6DLEeM3IgKNoBlJPp94WSJkgvwTM64rXw049ZkYenl9jwKlcXEmA\
  1a4MNWoUElr6eh5k20djMZftCYTPUUPMxZUavcQy+cp6lfKonz6HIDe3+n3VOTOo8uu1a\
  SVfKQQzR+ZEwSaZQBrdQ==:
x-forwarded-for: 192.0.2.123
"@signature-params": ("signature";key="sig1" "x-forwarded-for")\
  ;created=1618884475;keyid="test-key-rsa";alg="rsa-v1_5-sha256"
~~~

And a signature output value of:

~~~
:NgQsRJwOL/EgoRXdcmHMOLZM+KWqLDsO76CrqoiLH279VJs9Fj6bn4V+perAEUbHBEMFCb\
l6tucEVgKrU+5IIyDMBI85FExQeuBrNPALczjCdxne6LUoBcWBAk8NoRyjfd++DXIAjAZcf\
/hBUXLll+5veI0ynzBRFTZ4v8AbluYODjJlSprYEwUb2ndbFr12vzgIpy0uTQCslN+3rUUZ\
+lQWlrILvbR0CIvtGwk2+hE0dTRAG0R3wmlR24mhSqiE5RADyoSWQVjVxntp98XHAB6MZE9\
2bbu2a8Uo951Hvah03XHWEk/WiYdq+mt3hwXVPLXlBU9DWCo2AaYD/rkXtQ==:
~~~

These values are added to the HTTP request message by the proxy. The different signature values are wrapped onto separate lines to increase human-readability of the result.

~~~ http-message
X-Forwarded-For: 192.0.2.123
Signature-Input: sig1=("@request-target" "host" "date" "cache-control" \
    "x-empty-header" "x-example");created=1618884475\
    ;keyid="test-key-rsa-pss", \
  proxy_sig=("signature";key="sig1" "x-forwarded-for");created=1618884480\
    ;keyid="test-key-rsa";alg="rsa-v1_5-sha256"
Signature: sig1=:H00a6KdNCRWgOWBMvuRtxh6c/wrVxwt2p5KyqBJqmtPbNTd980hWwk\
    UE6H4NWiTs5f2Ef0qJ3iypXT2bR9Pc+PVU9U2gAzTcZKK8MDJLjYKfaE835zg/9sOdG\
    R+tlRJ1cbCoWMVoCgEPi4t6QewbI0xgdx8AmP5ItTunYmhe8G0JR42lfvz60+szb8Sp\
    wJEmkMPr5dBOz6DLEeM3IgKNoBlJPp94WSJkgvwTM64rXw049ZkYenl9jwKlcXEmA1a\
    4MNWoUElr6eh5k20djMZftCYTPUUPMxZUavcQy+cp6lfKonz6HIDe3+n3VOTOo8uu1a\
    SVfKQQzR+ZEwSaZQBrdQ==:, \
  proxy_sig=:NgQsRJwOL/EgoRXdcmHMOLZM+KWqLDsO76CrqoiLH279VJs9Fj6bn4V+pe\
    rAEUbHBEMFCbl6tucEVgKrU+5IIyDMBI85FExQeuBrNPALczjCdxne6LUoBcWBAk8No\
    Ryjfd++DXIAjAZcf/hBUXLll+5veI0ynzBRFTZ4v8AbluYODjJlSprYEwUb2ndbFr12\
    vzgIpy0uTQCslN+3rUUZ+lQWlrILvbR0CIvtGwk2+hE0dTRAG0R3wmlR24mhSqiE5RA\
    DyoSWQVjVxntp98XHAB6MZE92bbu2a8Uo951Hvah03XHWEk/WiYdq+mt3hwXVPLXlBU\
    9DWCo2AaYD/rkXtQ==:
~~~

The proxy's signature and the client's original signature can be verified independently for the same message, depending on the needs of the application.

# IANA Considerations {#iana}

## HTTP Signature Algorithms Registry {#hsa-registry}

This document defines HTTP Signature Algorithms, for which IANA is asked to create and maintain a new registry titled "HTTP Signature Algorithms".  Initial values for this registry are given in {{iana-hsa-contents}}.  Future assignments and modifications to existing assignment are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-hsa-template}}.

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

#### rsa-pss-sha512

{: vspace="0"}
Algorithm Name:
: `rsa-pss-sha512`

Status:
: Active

Definition:
: RSASSA-PSS using SHA-256

Specification document(s):
: \[\[This document\]\], {{method-rsa-pss-sha512}}

#### rsa-v1_5-sha256

{: vspace="0"}
Algorithm Name:
: `rsa-v1_5-sha256`

Status:
: Active

Description:
: RSASSA-PKCS1-v1_5 using SHA-256

Specification document(s):
: \[\[This document\]\], {{method-rsa-v1_5-sha256}}

#### hmac-sha256

{: vspace="0"}
Algorithm Name:
: `hmac-sha256`

Status:
: Active

Description:
: HMAC using SHA-256

Specification document(s):
: \[\[This document\]\], {{method-hmac-sha256}}


#### ecdsa-p256-sha256

{: vspace="0"}
Algorithm Name:
: `ecdsa-p256-sha256`

Status:
: Active

Description:
: ECDSA using curve P-256 DSS and SHA-256

Specification document(s):
: \[\[This document\]\], {{method-ecdsa-p256-sha256}}

## HTTP Signature Metadata Parameters Registry {#param-registry}

This document defines the `Signature-Input` Structured Header, whose member values may have parameters containing metadata about a message signature. IANA is asked to create and maintain a new registry titled "HTTP Signature Metadata Parameters" to record and maintain the set of parameters defined for use with member values in the `Signature-Input` Structured Header. Initial values for this registry are given in {{iana-param-contents}}.  Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-param-template}}.

### Registration Template {#iana-param-template}

### Initial Contents {#iana-param-contents}

The table below contains the initial contents of the HTTP Signature Metadata Parameters Registry.  Each row in the table represents a distinct entry in the registry.

|Name|Status|Reference(s)|
|--- |--- |--- |
|`alg`|Active | {{signature-params}} of this document|
|`created`|Active   | {{signature-params}} of this document|
|`expires`|Active   | {{signature-params}} of this document|
|`keyid`|Active     | {{signature-params}} of this document|
|`nonce`|Active    | {{signature-params}} of this document|
{: title="Initial contents of the HTTP Signature Metadata Parameters Registry." }

## HTTP Signature Specialty Content Identifiers Registry {#content-registry}

This document defines a method for canonicalizing HTTP message content, including content that can be generated from the context of the HTTP message outside of the HTTP headers. This content is identified by a unique key.  IANA is asked to create and maintain a new registry typed "HTTP Signature Specialty Content Identifiers" to record and maintain the set of non-header content identifiers and their canonicalization method. Initial values for this registry are given in {{iana-content-contents}}.  Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-content-template}}.

### Registration Template {#iana-content-template}

### Initial Contents {#iana-content-contents}

The table below contains the initial contents of the HTTP Signature Specialty Content Identifiers Registry.

|Name|Status|Reference(s)|
|--- |--- |--- |
|`@request-target`|Active   | {{content-request-target}} of this document|
|`@signature-params`|Active   | {{signature-params}} of this document|
{: title="Initial contents of the HTTP Signature Specialty Content Identifiers Registry." }

# Security Considerations {#security}

(( TODO: need to dive deeper on this section; not sure how much of what's referenced below is actually applicable, or if it covers everything we need to worry about. ))

(( TODO: Should provide some recommendations on how to determine what content needs to be signed for a given use case. ))

There are a number of security considerations to take into account when implementing or utilizing this specification.  A thorough security analysis of this protocol, including its strengths and weaknesses, can be found in {{WP-HTTP-Sig-Audit}}.

--- back

# Detecting HTTP Message Signatures {#detection}

There have been many attempts to create signed HTTP messages in the past, including other non-standard definitions of the `Signature` header used within this specification. It is recommended that developers wishing to support both this specification and other historial drafts do so carefully and deliberately, as incompatibilities between this specification and various versions of other drafts could lead to problems.

It is recommended that implementers first detect and validate the `Signature-Input` header defined in this specification to detect that this standard is in use and not an alternative. If the `Signature-Input` header is present, all `Signature` headers can be parsed and interpreted in the context of this draft.

# Examples

## Example Keys {#example-keys}

This section provides cryptographic keys that are referenced in example signatures throughout this document.  These keys MUST NOT be used for any purpose other than testing.

The key identifiers for each key are used throughout the examples in this specification. It is assumed for these examples that the signer and verifier can unambiguously dereference all key identifiers used here, and that the keys and algorithms used are appropriate for the context in which the signature is presented. 

### Example Key RSA test {#example-key-rsa-test}

The following key is a 2048-bit RSA public and private key pair, referred to in this document
as `test-key-rsa`:

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

### Example Key RSA PSS test {#example-key-rsa-pss-test}

The following key is a 2048-bit RSA public and private key pair, referred to in this document
as `test-key-rsa-pss`:

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

## Test Cases

This section provides non-normative examples that may be used as test cases to validate implementation correctness. These examples are based on the following HTTP message:

~~~ http-message
POST /foo?param=value&pet=dog HTTP/1.1
Host: example.com
Date: Tue, 20 Apr 2021 02:07:55 GMT
Content-Type: application/json
Digest: SHA-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
Content-Length: 18

{"hello": "world"}
~~~

### Minimal Signature Header using rsa-pss-sha512

This example presents a minimal `Signature-Input` and `Signature` header for a signature using the `rsa-pss-sha512` algorithm, covering none
of the content of the HTTP message request but providing a timestamped signature proof of possession of the key.

The corresponding signature input is:

~~~
"@signature-params": ();created=1618884475;keyid="test-key-rsa-pss"\
  ;alg="rsa-pss-sha512"
~~~

This results in the following `Signature-Input` and `Signature` headers being added to the message:

~~~ http-message
Signature-Input: sig1=();created=1618884475;keyid="test-key-rsa-pss"\
  ;alg="rsa-pss-sha512"
Signature: sig1=:qGKjr1213+iZCU1MCV8w2NTr/HvMGWYDzpqAWx7SrPE1y6gOkIQ3k2\
  GlZDu9KnKnLN6LKX0JRa2M5vU9v/b0GjV0WSInMMKQJExJ/e9Y9K8q2eE0G9saGebEaWd\
  R3Ao47odxLh95hBtejKIdiUBmQcQSAzAkoQ4aOZgvrHgkmvQDZQL0w30+8lMz3VglmN73\
  CKp/ijZemO1iPdNwrdhAtDvj9OdFVJ/wiUECfU78aQWkQocvwrZXTmHCX9BMVUHGneXMY\
  NQ0Y8umEHjxpnnLLvxUbw2KZrflp+l6m7WlhwXGJ15eAt1+mImanxUCtaKQJvEfcnOQ0S\
  2jHysSRLheTA==:
~~~

### Header Coverage

This example covers all the specified headers in the example message.

The corresponding signature input is:

~~~
"host": example.com
"date": Tue, 20 Apr 2021 02:07:55 GMT
"content-type": application/json
"@signature-params": ("host" "date" "content-type");created=1618884475\
  ;keyid="test-key-rsa-pss"
~~~


This results in the following `Signature-Input` and `Signature` headers being added to the message:


~~~
Signature-Input: sig1=("host" "date" "content-type");created=1618884475\
  ;keyid="test-key-rsa-pss"
Signature: sig1=:NtIKWuXjr4SBEXj97gbick4O95ff378I0CZOa2VnIeEXZ1itzAdqTp\
  SvG91XYrq5CfxCmk8zz1Zg7ZGYD+ngJyVn805r73rh2eFCPO+ZXDs45Is/Ex8srzGC9sf\
  VZfqeEfApRFFe5yXDmANVUwzFWCEnGM6+SJVmWl1/jyEn45qA6Hw+ZDHbrbp6qvD4N0S9\
  2jlPyVVEh/SmCwnkeNiBgnbt+E0K5wCFNHPbo4X1Tj406W+bTtnKzaoKxBWKW8aIQ7rg9\
  2zqE1oqBRjqtRi5/Q6P5ZYYGGINKzNyV3UjZtxeZNnNJ+MAnWS0mofFqcZHVgSU/1wUzP\
  7MhzOKLca1Yg==:
~~~

### Full Coverage

This example covers all headers in the example message plus the request target and message body digest.

The corresponding signature input is:

~~~
"@request-target": post /foo?param=value&pet=dog
"host": example.com
"date": Tue, 20 Apr 2021 02:07:55 GMT
"content-type": application/json
"digest": SHA-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
"content-length": 18
"@signature-params": ("@request-target" "host" "date" "content-type" \
  "digest" "content-length");created=1618884475\
  ;keyid="test-key-rsa-pss"
~~~

This results in the following `Signature-Input` and `Signature` headers being added to the message:

~~~
Signature-Input: sig1=("@request-target" "host" "date" "content-type" \
  "digest" "content-length");created=1618884475\
  ;keyid="test-key-rsa-pss"
Signature: sig1=:QNPZtqAGWN1YMtsLJ1oyQMLg9TuIwjsIBESTo1/YXUsG+6Sl1uKUdT\
  e9xswwrc3Ui3gUd4/tLv48NGih2TRDc1AWbEQDuy6pjroxSPtFjquubqzbszxit1arPNh\
  ONnyR/8yuIh3bOXfc/NYJ3KLNaWR6MKrGinCYKTNwrX/0V67EMdSgd5HHnW5xHFgKfRCj\
  rG3ncV+jbaeSPJ8e96RZgr8slcdwmqXdiwiIBCQDKRIQ3U2muJWvxyjV/IYhCTwAXJaUz\
  sQPKzR5QWelXEVdHyv4WIB2lKaYh7mAsz0/ANxFYRRSp2Joms0OAnIAFX9kKCSp4p15/Q\
  8L9vSIGNpQtw==:
~~~

# Acknowledgements {#acknowledgements}
{:numbered="false"}

This specification was initially based on the draft-cavage-http-signatures internet draft.  The editors would like to thank the authors of that draft, Mark Cavage and Manu Sporny, for their work on that draft and their continuing contributions.

The editors would also like to thank the following individuals for feedback, insight, and implementation of this draft and its predecessors (in alphabetical order):
Mark Adamcin,
Mark Allen,
Paul Annesley,
Karl Böhlmark,
Stéphane Bortzmeyer,
Sarven Capadisli,
Liam Dennehy,
ductm54,
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
