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

HTTP permits and sometimes requires intermediaries to transform messages in a variety of ways.  This may result in a recipient receiving a message that is not bitwise equivalent to the message that was oringally sent.  In such a case, the recipient will be unable to verify a signature over the raw bytes of the sender's HTTP message, as verifying digital signatures or MACs requires both signer and verifier to have the exact same signed content.  Since the raw bytes of the message cannot be relied upon as signed content, the signer and verifier must derive the signed content from their respective versions of the message, via a mechanism that is resilient to safe changes that do not alter the meaning of the message.

For a variety of reasons, it is impractical to strictly define what constitutes a safe change versus an unsafe one.  Applications use HTTP in a wide variety of ways, and may disagree on whether a particular piece of information in a message (e.g., the body, or the `Date` header field) is relevant.  Thus a general purpose solution must provide signers with some degree of control over which message content is signed.

HTTP applications may be running in environments that do not provide complete access to or control over HTTP messages (such as a web browser's JavaScript environment), or may be using libraries that abstract away the details of the protocol (such as [the Java HTTPClient library](https://openjdk.java.net/groups/net/httpclient/intro.html)).  These applications need to be able to generate and verify signatures despite incomplete knowledge of the HTTP message.

## HTTP Message Transformations {#about_sigs}

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

The term "Unix time" is defined by {{POSIX.1}} [section 4.16](http://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html#tag_04_16).

This document contains non-normative examples of partial and complete HTTP messages.  To improve readability, header fields may be split into multiple lines, using the `obs-fold` syntax.  This syntax is deprecated in [MESSAGING], and senders MUST NOT generate messages that include it.

Additionally, some examples use '\\' line wrapping for long values that contain no whitespace, as per {{!RFC8792}}.

## Application of HTTP Message Signatures {#application}

HTTP Message Signatures are designed to be a general-purpose security mechanism applicable in a wide variety of circumstances and applications. In order to properly and safely apply HTTP Message Signatures, an application or profile of this specification MUST specify all of the following items:

- The set of [content identifiers](#content-identifiers) that are expected and required. For example, an authorization protocol would mandate that the `Authorization` header be covered to protect the authorization credentials, as well as a `*created` field to allow replay detection.
- A means of retrieving the key material used to verify the signature. An application will usually use the `keyid` parameter of the `Signature-Input` header value and define rules for resolving a key from there.
- A means of determining the signature algorithm used to verify the signature content is appropriate for the key material.
- A means of determining that a given key and algorithm presented in the request are appropriate for the request being made. For example, a server expecting only ECDSA signatures should know to reject any RSA signatures; or a server expecting asymmetric cryptography should know to reject any symmetric cryptography.

The details of this kind of profiling are the purview of the application and outside the scope of this specification.

# Identifying and Canonicalizing Content {#content-identifiers}

In order to allow signers and verifiers to establish which content is covered by a signature, this document defines content identifiers for data items covered by an HTTP Message Signature.

Some content within HTTP messages can undergo transformations that change the bitwise value without altering meaning of the content (for example, the merging together of header fields with the same name).  Message content must therefore be canonicalized before it is signed, to ensure that a signature can be verified despite such intermediary transformations. This document defines rules for each content identifier that transform the identifier's associated content into such a canonical form.

Content identifiers are defined using production grammar defined by {{!RFC8941}} section 4.
The content identifier is an `sf-string` value. The content identifier
type MAY define parameters which are included using the `parameters` rule.

~~~
content-identifier = sf-string parameters
~~~

Note that this means the value of the identifier itself is encased in double quotes, with parameters following as a semicolon-separated list, such as `"cache-control"`, `"date"`, or `"@signature-params"`.

The following sections define content identifier types, their parameters, their associated content, and their canonicalization rules.

## HTTP Headers {#http-header}

The content identifier for an HTTP header is the lowercased form of its header field name. While HTTP header field names are case-insensitive, implementations MUST use lowercased field names (e.g., `content-type`, `date`, `etag`) when using them as content identifiers.

Unless overridden by additional parameters and rules, the HTTP header field value MUST be canonicalized with the following steps:

1. Create an ordered list of the field values of each instance of the header field in the message, in the order that they occur (or will occur) in the message.
2. Strip leading and trailing whitespace from each item in the list.
3. Concatenate the list items together, with a comma "," and space " " between each item. 

The resulting string is the canonicalized value.

### Canonicalized Structured HTTP Headers {#http-header-structured}

If value of the the HTTP header in question is a structured field {{!RFC8941}}, the content identifier MAY include the `sf` parameter. If this
parameter is included, the HTTP header value MUST be canonicalized using the rules specified in {{!RFC8941}} section 4. Note that this process
will replace any optional whitespace with a single space.

The resulting string is used as the field value input in {{http-header}}.

### Canonicalization Examples

This section contains non-normative examples of canonicalized values for header fields, given the following example HTTP message:

~~~ http-message
HTTP/1.1 200 OK
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

An individual member in the value of a Dictionary Structured Field is canonicalized by applying the serialization algorithm described in Section 4.1.2 of {{!RFC8941}} on a Dictionary containing only that member.

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

A list prefix value is canonicalized by applying the serialization algorithm described in Section 4.1.1 of {{!RFC8941}} on a List containing only the first N members as specified in the list prefix, in the order they appear in the original List.

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


## Specialty Content Fields

Content not found in an HTTP header can be included in the signature base string by defining a content identifier and the canonicalization method for its content.

To differentiate specialty content identifiers from HTTP headers, specialty content identifiers MUST start with the "at" `@` character. This specification defines the following specialty content identifiers:

@request-target
: The target request endpoint. {{content-request-target}}

@signature-params
: The signature metadata parameters for this signature. {{content-signature-params}}

Additional specialty content identifiers MAY be defined and registered in the HTTP Signatures Specialty Content Identifier Registry. {{content-registry}}

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

### Signature Parameters {#content-signature-params}

The signature parameters special content is identified by the `@signature-params` identifier.

Its canonicalized value is the serialization of the signature parameters for this signature, including the covered content list with all associated parameters. {{signature-metadata}}

Note that an HTTP message could contain multiple signatures, but only the signature parameters used for the current signature are included.

#### Canonicalization Examples

Given the following signature parameters:

|Property|Value|
|--- |--- |
|Algorithm|`rsa-pss-SHA256`|
|Covered Content|`@request-target`, `host`, `date`, `cache-control`, `x-emptyheader`, `x-example`, `x-dictionary;key=b`, `x-dictionary;key=a`, `x-list;prefix=3`|
|Creation Time|`1402174295`|
|Expiration Time|`1402174595`|
|Verification Key Material|The public key provided in {{example-key-rsa-test}} and identified by the `keyid` value "test-key-a".|

The signature parameter value is defined as:

~~~
# NOTE: '\' line wrapping per RFC 8792
"@signature-params": ("@request-target" "host" "date" "cache-control" "x-empty-header" \
   "x-example" "x-dictionary";key=b "x-dictionary";key=a "x-list";prefix=3); 
   \keyid="test-key-a"; alg="rsa-pss-SHA256"; created=1402170695; expires=1402170995
~~~

## Create the Signature Input {#create-sig-input}

The Signature Input is a US-ASCII string containing the content is covered by the signature. To create it, the signer or verifier concatenates together entries for each identifier in the signature's Covered Content in the order it occurs in the covered content list using the following algorithm:

1. Let the output be an empty string.

2. For each covered content item in the covered content list:

    1. Append the identifier for the covered content serialized according to the `content-identifier` rule.

    2. Append a single colon `":"`

    3. Append a single space `" "`

    4. Append the covered content's canonicalized value, as defined by the covered content type. {{content-identifiers}}

    5. Append a single newline `"\\n"`

3. Append the signature parameters {{content-signature-params}} as follows:

    1. Append the identifier for the signature parameters serialized according to the `content-identifier` rule, `"@signature-params"`

    2. Append a single colon `":"`

    3. Append a single space `" "`

    4. Append the signature parameters' canonicalized value as defined in {{content-signature-params}}

4. Return the output string.    

If Covered Content contains an identifier for a header field that is malformed or is not present in the message, such as a header that does not exist, the implementation MUST produce an error.

If Covered Content contains an identifier for a Dictionary member that references a header field using the `key` parameter that is not present, is malformed in the message, or is not a Dictionary Structured Field, the implementation MUST produce an error. If the header field value does not contain the specified member, the implementation MUST produce an error.

If Covered Content contains an identifier for a List Prefix that references a header field using the `prefix` parameter that is not present, is malformed in the message, or is not a List Structured Field, the implementation MUST produce an error. If the header field value contains fewer than the specified number of members, the implementation MUST produce an error.

For the non-normative example Signature metadata in {{example-metadata}}, the corresponding Signature Input is:

~~~
# NOTE: '\' line wrapping per RFC 8792
"@request-target": get /foo
"host": example.org
"date": Tue, 07 Jun 2014 20:51:35 GMT
"cache-control": max-age=60, must-revalidate
"x-emptyheader": 
"x-example": Example header with some whitespace.
"x-dictionary";key=b: 2
"x-dictionary";key=a: 1
"x-list";prefix=3: (a, b, c)
"@signature-params": ("@request-target" "host" "date" "cache-control" "x-empty-header" "x-example" \
  "x-dictionary";key=b "x-dictionary";key=b "x-list";prefix=3); keyid="test-key-a"; \
  created=1402170695; expires=1402170995
~~~
{: title="Non-normative example Signature Input" artwork-name="example-sig-input" #example-sig-input}

# HTTP Message Signatures {#message-signatures}

An HTTP Message Signature is a signature over a string generated from a subset of the content in an HTTP message and metadata about the signature itself.  When successfully verified against an HTTP message, it provides cryptographic proof that with respect to the subset of content that was signed, the message is semantically equivalent to the message for which the signature was generated.

## Signature Metadata {#signature-metadata}

HTTP Message Signatures have metadata properties that provide information regarding the signature's generation and/or verification.  The following metadata properties are defined:

{: vspace="0"}
Algorithm:
: An HTTP Signature Algorithm defined in the HTTP Signature Algorithms Registry defined in this document, represented as a string. It describes the signing and verification algorithms for the signature.

Key Material:
: The key material required to create or verify the signature. 

Creation Time:
: A timestamp representing the point in time that the signature was generated, represented as an integer. Sub-second precision is not supported. A signature's Creation Time MAY be undefined, indicating that it is unknown.

Expiration Time:
: A timestamp representing the point in time at which the signature expires, represented as an integer. An expired signature always fails verification. A signature's Expiration Time MAY be undefined, indicating that the signature does not expire.

Covered Content:
: An ordered list of content identifiers (Section 2) that indicates the metadata and message content that is covered by the signature. This list MUST NOT include the `@signature-params` content identifier.

The signature metadata is serialized using the rules in {{!RFC8941}} section 4 as follows:

1. Let the output be an empty string.
2. Serialize the content identifiers as an ordered `inner-list` according to {{!RFC8941}} section 4.1.1.1 and append this to the output.
3. Append the signature metadata as parameters according to {{!RFC8941}} section 4.1.1.2 in the any order, skipping fields that are not available:
   * `alg`: Algorithm as an `sf-string` value.
   * `keyid`: Verification Key Material as an `sf-string` value.
   * `created`: Creation Time as an `sf-integer` timestamp value.
   * `expires`: Expiration Time as an `sf-integer` timestamp value.
   
Note that the `inner-list` serialization is used instead of the `sf-list` serialization in order to facilitate this value's inclusion in the `Signature-Input` header's dictionary, as discussed in {{signature-input-header}}.

The {{example-metadata}} values would be serialized as follows:

~~~
# NOTE: '\' line wrapping per RFC 8792
("@request-target" "host" "date" "cache-control" "x-empty-header" "x-example"); \
  keyid="test-key-a"; alg="rsa-pss-SHA256"; created=1402170695; expires=1402170995
~~~

## Creating a Signature {#create}

In order to create a signature, a signer completes the following process:

1. Choose signature metadata properties, including algorithm and key material {{choose-metadata}}
2. Create the signature input from the HTTP request message {{create-sig-input}}
3. Sign the signature input to produce the signature output {{sign-sig-input}}

### Choose and Set Signature Metadata Properties {#choose-metadata}

1. The signer chooses an HTTP signature algorithm and key material for signing. The signer MUST choose key material that is appropriate 
    for the signature's algorithm, and that conforms to any requirements defined by the algorithm, such as key size or format. The 
    mechanism by which the signer chooses the algorithm and key material is out of scope for this document.

2. The signer sets the signature's creation time to the current time.

3. If applicable, the signer sets the signature's expiration time property to the time at which the signature is to expire.

5. The signer creates an ordered list of content identifiers representing the message content and signature metadata to be covered by the signature, and assigns this list as the signature's Covered Content.
   * Each identifier MUST be one of those defined in .
   * Signers SHOULD include `@request-target` in the list.
   * Signers SHOULD include a date stamp in some form, such as using the `date` header. Alternatively, the `created` signature metadata parameter can fulfil this role.
   * Further guidance on what to include in this list and in what order is out of scope for this document. However, note that the list order is significant and once established for a given signature it MUST be preserved for that signature.
   * Note that the signature metadata is not included in the explicit list of covered content identifiers, but its value is included in the `@signature-params` specialty identifier. 

For example, given the following HTTP message:

~~~ http-message
GET /foo HTTP/1.1
Host: example.org
Date: Sat, 07 Jun 2014 20:51:35 GMT
X-Example: Example header
        with some whitespace.
X-EmptyHeader:
X-Dictionary: a=1, b=2
X-List: (a b c d)
Cache-Control: max-age=60
Cache-Control: must-revalidate
~~~

The following table presents a non-normative example of metadata values that a signer may choose:

|Property|Value|
|--- |--- |
|Covered Content|`@request-target`, `host`, `date`, `cache-control`, `x-emptyheader`, `x-example`, `x-dictionary;key=b`, `x-dictionary;key=a`, `x-list;prefix=3`|
|Creation Time|`1402174295`|
|Expiration Time|`1402174595`|
|Verification Key Material|The public key provided in {{example-key-rsa-test}} and identified by the `keyid` value "test-key-a".|
{: title="Non-normative example metadata values" #example-metadata}

### Sign the Signature Input {#sign-sig-input}

The signer signs the signature input with the signing algorithm described in {{signature-methods}} using the key material chosen by the signer.
The signer then encodes the result of that operation as a Base64-encoded string {{?RFC4648}}.  This string is the signature output value.

For the non-normative example signature metadata in {{choose-metadata}} and Signature Input in {{example-sig-input}}, the corresponding signature value is:

~~~
# NOTE: '\' line wrapping per RFC 8792
K2qGT5srn2OGbOIDzQ6kYT+ruaycnDAAUpKv+ePFfD0RAxn/1BUeZx/Kdrq32DrfakQ6b\
PsvB9aqZqognNT6be4olHROIkeV879RrsrObury8L9SCEibeoHyqU/yCjphSmEdd7WD+z\
rchK57quskKwRefy2iEC5S2uAH0EPyOZKWlvbKmKu5q4CaB8X/I5/+HLZLGvDiezqi6/7\
p2Gngf5hwZ0lSdy39vyNMaaAT0tKo6nuVw0S1MVg1Q7MpWYZs0soHjttq0uLIA3DIbQfL\
iIvK6/l0BdWTU7+2uQj7lBkQAsFZHoA96ZZgFquQrXRlmYOh+Hx5D9fJkXcXe5tmAg==
~~~
{: title="Non-normative example signature value" #example-sig-value}


## Verifying a Signature {#verify}

In order to verify a signature, a verifier MUST follow the following algorithm:

1. Examine the signature's parameters to confirm that the signature meets the requirements described 
    in this document, as well as any additional requirements defined by the application such as which 
    contents are required to be covered by the signature. {{verify-requirements}}
2. Use the received HTTP message and the signature's metadata to recreate the signature input, using 
    the process described in {{create-sig-input}}. The value of the `@signature-params` input is
    the value of the signature input header field for this signature serialized according to the rules described
    in {{content-signature-params}}, not including the signature's label.
3. Determine the verification key material for this signature. If the key material is known through external
    means such as static configuration or external protocol negotiation, the verifier will use that. If the key is
    identified in the signature parameters, the verifier will dereference this to appropriate key material to use 
    with the signature. The verifier has to determine the trustworthiness of the key material for the context
    in which the signature is presented.
4. Determine the algorithm to apply for verification:
    1. If the algorithm is known through external means such as static configuration or external protocol
        negotiation, the verifier will use this algorithm.
    2. If the algorithm is explicitly stated in the signature parameters using a value from the
        HTTP Message Signatures registry, the verifier will use the referenced algorithm.
    3. If the algorithm can be determined from the keying material, such as through an algorithm field
        on the key value itself, the verifier will use this algorithm.
5. If the key material is appropriate for the algorithm, apply the verification algorithm to the signature,
    signature input, signature parameters, key material, and algorithm.



### Enforcing Application Requirements {#verify-requirements}

The verification requirements specified in this document are intended as a baseline set of restrictions that are generally applicable to all use cases.  Applications using HTTP Message Signatures MAY impose requirements above and beyond those specified by this document, as appropriate for their use case.

Some non-normative examples of additional requirements an application might define are:

- Requiring a specific set of header fields to be signed (e.g., Authorization, Digest).
- Enforcing a maximum signature age.
- Prohibiting the use of certain algorithms, or mandating the use of an algorithm.
- Requiring keys to be of a certain size (e.g., 2048 bits vs. 1024 bits).

Application-specific requirements are expected and encouraged.  When an application defines additional requirements, it MUST enforce them during the signature verification process, and signature verification MUST fail if the signature does not conform to the application's requirements.

Applications MUST enforce the requirements defined in this document.  Regardless of use case, applications MUST NOT accept signatures that do not conform to these requirements.

## Signature Methods {#signature-methods}

Message signatures MAY use any cryptographic signing or MAC method that allows for the signing of the signature input string.

Signatures are generated from and verified against the byte values of the signature input string defined in {{create-sig-input}}.

### RSASSA-PSS using SHA-512 {#method-rsa-pss-sha256}

To sign using this algorithm, the signer applies the `RSASSA-PSS-SIGN (K, M)` function {{RFC8017}} with the signer's private signing key (`K`) and
the signature input string (`M`) {{create-sig-input}}. The hash function used is SHA-512 {{RFC6234}}. The resulting signed content (`S`) is
Base64-encoded as described in {{sign-sig-input}}. The resulting encoded value is the HTTP message signature output.

To verify using this algorithm, the verifier applies the `RSASSA-PSS-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key material (`(n, e)`).
The verifier re-creates the signature input string defined in {{create-sig-input}} (`M`). The verifier decodes the HTTP message signature from Base64 as 
described in {{verify}} to give the signature to be verified (`S`). The hash function used is SHA-512 {{RFC6234}}. Applying the function gives the 
signature verification result.

### RSASSA-PKCS1-v1_5 using SHA-256 {#method-rsa-v1_5-sha256}

To sign using this algorithm, the signer applies the `RSASSA-PKCS1-V1_5-SIGN (K, M)` function {{RFC8017}} to signer's private signing key (`K`) and
the signature input string (`M`) {{create-sig-input}}. The hash function used is SHA-256 {{RFC6234}}. The resulting signed content (`S`) is
Base64-encoded as described in {{sign-sig-input}}. The resulting encoded value is the HTTP message signature output.

To verify using this algorithm, the verifier applies the `RSASSA-PKCS1-V1_5-VERIFY ((n, e), M, S)` function {{RFC8017}} using the public key material (`(n, e)`).
The verifier re-creates the signature input string defined in {{create-sig-input}} (`M`). The verifier decodes the HTTP message signature from Base64 as 
described in {{verify}} to give the signature to be verified (`S`). The hash function used is SHA-256 {{RFC6234}}. Applying the function gives the 
signature verification result.

### HMAC using SHA-256 {#method-hmac-sha256}

To sign and verify using this algorithm, the signer applies the `HMAC` function {{RFC2104}} with the shared signing key (`K`) and
the signature input string (`text`) {{create-sig-input}}. The hash function used is SHA-256 {{RFC6234}}. For signing, the resulting signed content is
Base64-encoded as described in {{sign-sig-input}}. The resulting encoded value is the HTTP message signature output. For verification, 
the verifier decodes the HTTP message signature from Base64 as described in {{verify}} to give the signature to be compared to the output of the
HMAC function.

### ECDSA using curve P-256 DSS and SHA-256 {#method-ecdsa-p256-sha256}

To sign using this algorithm, the signer applies the `ECDSA` algorithm {{FIPS186-4}} using curve P-256 with signer's private signing key and
the signature input string {{create-sig-input}}. The hash function used is SHA-256 {{RFC6234}}. The resulting signed content is
Base64-encoded as described in {{sign-sig-input}}. The resulting encoded value is the HTTP message signature output.

To verify using this algorithm, the verifier applies the `ECDSA` algorithm {{FIPS186-4}} using the public key material.
The verifier re-creates the signature input string defined in {{create-sig-input}}. The verifier decodes the HTTP message signature from Base64 as 
described in {{verify}} to give the signature to be verified. The hash function used is SHA-256 {{RFC6234}}. Applying the verification algorithm gives the 
signature verification result.

### JSON Web Signature (JWS) algorithms {#method-jose}

If the signing algorithm is a JOSE signing algorithm from the JSON Web Signature and Encryption Algorithms Registry established by {{RFC7518}}, the 
JWS algorithm definition determines the signature and hashing algorithms to apply for both signing and verification. 

For both signing and verification, the HTTP messages signature input string {{create-sig-input}} is used as the entire "JWS Signing Input". The JWS 
Header defined in {{RFC7517}} is not used, nor is the input string first encoded in Base64 before applying the algorithm.

The JWS algorithm MUST NOT be `none` and MUST NOT be any algorithm with a JOSE Implementation Requirement of `Prohibited`.

# Including a Message Signature in a Message
Message signatures can be included within an HTTP message via the `Signature-Input` and `Signature` HTTP header fields, both defined within this specification. The `Signature` HTTP header field contains signature values, while the `Signature-Input` HTTP header field identifies the Covered Content and metadata that describe how each signature was generated.

## The 'Signature-Input' HTTP Header {#signature-input-header}
The `Signature-Input` HTTP header field is a Dictionary Structured Header {{!RFC8941}} containing the metadata for zero or more message signatures generated from content within the HTTP message. Each member describes a single message signature. The member's name is an identifier that uniquely identifies the message signature within the context of the HTTP message. The member's value is the serialization of the covered content including all signature metadata parameters, described in {{signature-metadata}}.

~~~
# NOTE: '\' line wrapping per RFC 8792
Signature-Input: sig1=("@request-target" "host" "date"
    "cache-control" "x-empty-header" "x-example"); keyid="test-key-a";
    alg="rsa-pss-SHA256"; created=1402170695; expires=1402170995
~~~

To facilitate signature validation, the `Signature-Input` header MUST contain the same serialization value used in generating the signature input.

## The 'Signature' HTTP Header {#signature-header}
The `Signature` HTTP header field is a Dictionary Structured Header {{!RFC8941}} containing zero or more message signatures generated from content within the HTTP message. Each member's name is a signature identifier that is present as a member name in the `Signature-Input` Structured Header within the HTTP message. Each member's value is a Byte Sequence containing the signature value for the message signature identified by the member name. Any member in the `Signature` HTTP header field that does not have a corresponding member in the HTTP message's `Signature-Input` HTTP header field MUST be ignored.

~~~
# NOTE: '\' line wrapping per RFC 8792
Signature: sig1=:K2qGT5srn2OGbOIDzQ6kYT+ruaycnDAAUpKv+ePFfD0RAxn/1BUe\
    Zx/Kdrq32DrfakQ6bPsvB9aqZqognNT6be4olHROIkeV879RrsrObury8L9SCEibe\
    oHyqU/yCjphSmEdd7WD+zrchK57quskKwRefy2iEC5S2uAH0EPyOZKWlvbKmKu5q4\
    CaB8X/I5/+HLZLGvDiezqi6/7p2Gngf5hwZ0lSdy39vyNMaaAT0tKo6nuVw0S1MVg\
    1Q7MpWYZs0soHjttq0uLIA3DIbQfLiIvK6/l0BdWTU7+2uQj7lBkQAsFZHoA96ZZg\
    FquQrXRlmYOh+Hx5D9fJkXcXe5tmAg==:
~~~

## Examples

The following is a non-normative example of `Signature-Input` and `Signature` HTTP header fields representing the signature in {{example-sig-value}}:

~~~ http-message
# NOTE: '\' line wrapping per RFC 8792

Signature-Input: sig1=("@request-target" "host" "date"
    "cache-control" "x-empty-header" "x-example"); keyid="test-key-a";
    alg="rsa-pss-SHA256"; created=1402170695; expires=1402170995
Signature: sig1=:K2qGT5srn2OGbOIDzQ6kYT+ruaycnDAAUpKv+ePFfD0RAxn/1BUe\
    Zx/Kdrq32DrfakQ6bPsvB9aqZqognNT6be4olHROIkeV879RrsrObury8L9SCEibe\
    oHyqU/yCjphSmEdd7WD+zrchK57quskKwRefy2iEC5S2uAH0EPyOZKWlvbKmKu5q4\
    CaB8X/I5/+HLZLGvDiezqi6/7p2Gngf5hwZ0lSdy39vyNMaaAT0tKo6nuVw0S1MVg\
    1Q7MpWYZs0soHjttq0uLIA3DIbQfLiIvK6/l0BdWTU7+2uQj7lBkQAsFZHoA96ZZg\
    FquQrXRlmYOh+Hx5D9fJkXcXe5tmAg==:
~~~

Since `Signature-Input` and `Signature` are both defined as Dictionary Structured Headers, they can be used to easily include multiple signatures within the same HTTP message. For example, a signer may include multiple signatures signing the same content with different keys and/or algorithms to support verifiers with different capabilities, or a reverse proxy may include information about the client in header fields when forwarding the request to a service host, and may also include a signature over those fields and the client's signature. The following is a non-normative example of header fields a reverse proxy might add to a forwarded request that contains the signature in the above example:

~~~ http-message
# NOTE: '\' line wrapping per RFC 8792

X-Forwarded-For: 192.0.2.123
Signature-Input: reverse_proxy_sig=("host" "date"
    "signature";key=sig1 "x-forwarded-for"); keyid="test-key-a";
    alg="rsa-pss-SHA256"; created=1402170695; expires=1402170695
Signature: reverse_proxy_sig=:ON3HsnvuoTlX41xfcGWaOEVo1M3bJDRBOp0Pc/O\
    jAOWKQn0VMY0SvMMWXS7xG+xYVa152rRVAo6nMV7FS3rv0rR5MzXL8FCQ2A35DCEN\
    LOhEgj/S1IstEAEFsKmE9Bs7McBsCtJwQ3hMqdtFenkDffSoHOZOInkTYGafkoy78\
    l1VZvmb3Y4yf7McJwAvk2R3gwKRWiiRCw448Nt7JTWzhvEwbh7bN2swc/v3NJbg/w\
    JYyYVbelZx4IywuZnYFxgPl/qvqbAjeEVvaLKLgSMr11y+uzxCHoMnDUnTYhMrmOT\
    4O8lBLfRFOcoJPKBdoKg9U0a96U2mUug1bFOozEVYFg==:
~~~

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

#### rsa-pss-sha256

{: vspace="0"}
Algorithm Name:
: `rsa-pss-sha256`

Status:
: Active

Definition:
: RSASSA-PSS using SHA-256

Specification document(s):
: \[\[This document\]\] {{method-rsa-pss-sha256}}

#### rsa-v1_5-sha256

{: vspace="0"}
Algorithm Name:
: `rsa-v1_5-sha256`

Status:
: Active

Description:
: RSASSA-PKCS1-v1_5 using SHA-256

Specification document(s):
: \[\[This document\]\] {{method-rsa-v1_5-sha256}}

#### hmac-sha256

{: vspace="0"}
Algorithm Name:
: `hmac-sha256`

Status:
: Active

Description:
: HMAC using SHA-256

Specification document(s):
: \[\[This document\]\] {{method-hmac-sha256}}


#### ecdsa-p256-sha256

{: vspace="0"}
Algorithm Name:
: `ecdsa-p256-sha256`

Status:
: Active

Description:
: ECDSA using curve P-256 DSS and SHA-256

Specification document(s):
: \[\[This document\]\] {{method-ecdsa-p256-sha256}}

## HTTP Signature Metadata Parameters Registry {#param-registry}

This document defines the `Signature-Input` Structured Header, whose member values may have parameters containing metadata about a message signature. IANA is asked to create and maintain a new registry titled "HTTP Signature Metadata Parameters" to record and maintain the set of parameters defined for use with member values in the `Signature-Input` Structured Header. Initial values for this registry are given in {{iana-param-contents}}.  Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-param-template}}.

### Registration Template {#iana-param-template}

### Initial Contents {#iana-param-contents}

The table below contains the initial contents of the HTTP Signature Metadata Parameters Registry.  Each row in the table represents a distinct entry in the registry.

|Name|Status|Reference(s)|
|--- |--- |--- |
|`alg`|Active | {{signature-metadata}} of this document|
|`created`|Active   | {{signature-metadata}} of this document|
|`expires`|Active   | {{signature-metadata}} of this document|
|`keyid`|Active     | {{signature-metadata}} of this document|
{: title="Initial contents of the HTTP Signature Metadata Parameters Registry." }

## HTTP Signature Specialty Content Identifiers Registry {#content-registry}

This document defines a method for canonicalizing HTTP message content, including content that can be generated from the context of the HTTP message outside of the HTTP headers. This content is identified by a unique key.  IANA is asked to create and maintain a new registry typed "HTTP Signature Specialty Content Identifiers" to record and maintain the set of non-header content identifiers and their canonicalization method. Initial values for this registry are given in {{iana-content-contents}}.  Future assignments and modifications to existing assignments are to be made through the Expert Review registration policy {{?RFC8126}} and shall follow the template presented in {{iana-content-template}}.

### Registration Template {#iana-content-template}

### Initial Contents {#iana-content-contents}

The table below contains the initial contents of the HTTP Signature Specialty Content Identifiers Registry.

|Name|Status|Reference(s)|
|--- |--- |--- |
|`@request-target`|Active   | {{content-request-target}} of this document|
|`@signature-params`|Active   | {{content-signature-params}} of this document|
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

### Example Key RSA test {#example-key-rsa-test}

The following key is a 2048-bit RSA public and private key pair:

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

## Example keyid Values

The table below maps example `keyid` values to associated algorithms and/or keys.  These are example mappings that are valid only within the context of examples in examples within this and future documents that reference this section.  Unless otherwise specified, within the context of examples it should be assumed that the signer and verifier understand these `keyid` mappings.  These `keyid` values are not reserved, and deployments are free to use them, with these associations or others.

|keyid|Algorithm|Verification Key|
|--- |--- |---|
|`test-key-a`|`rsa-pss-sha256`|The public key specified in {{example-key-rsa-test}}|
|`test-key-b`|`rsa-v1_5-sha256`|The public key specified in {{example-key-rsa-test}}|

## Test Cases

This section provides non-normative examples that may be used as test cases to validate implementation correctness.  These examples are based on the following HTTP message:

~~~ http-message
POST /foo?param=value&pet=dog HTTP/1.1
Host: example.com
Date: Tue, 07 Jun 2014 20:51:35 GMT
Content-Type: application/json
Digest: SHA-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=
Content-Length: 18

{"hello": "world"}
~~~

### Signature Verification

#### Minimal Signature Header using rsa-pss-sha256

This presents a minimal `Signature-Input` and `Signature` header for a signature using the `rsa-pss-sha256` algorithm:

~~~ http-message
# NOTE: '\' line wrapping per RFC 8792

Signature: sig1=("date"); alg="rsa-pss-sha256"; keyid="test-key-b"
Signature: sig1=:HtXycCl97RBVkZi66ADKnC9c5eSSlb57GnQ4KFqNZplOpNfxqk62\
    JzZ484jXgLvoOTRaKfR4hwyxlcyb+BWkVasApQovBSdit9Ml/YmN2IvJDPncrlhPD\
    VDv36Z9/DiSO+RNHD7iLXugdXo1+MGRimW1RmYdenl/ITeb7rjfLZ4b9VNnLFtVWw\
    rjhAiwIqeLjodVImzVc5srrk19HMZNuUejK6I3/MyN3+3U8tIRW4LWzx6ZgGZUaEE\
    P0aBlBkt7Fj0Tt5/P5HNW/Sa/m8smxbOHnwzAJDa10PyjzdIbywlnWIIWtZKPPsoV\
    oKVopUWEU3TNhpWmaVhFrUL/O6SN3w==:
~~~

The corresponding signature metadata derived from this header field is:

|Property|Value|
|--- |--- |
|Algorithm|`rsa-pss-sha256`|
|Covered Content|`date`|
|Creation Time|Undefined|
|Expiration Time|Undefined|
|Verification Key Material|The public key specified in {{example-key-rsa-test}}.|


The corresponding Signature Input is:

~~~
"date": Tue, 07 Jun 2014 20:51:35 GMT
"@signature-params": ("date"); alg="rsa-pss-sha256"; keyid="test-key-b"
~~~

# Acknowledgements {#acknowledgements}
{:numbered="false"}

This specification was initially based on the draft-cavage-http-signatures internet draft.  The editors would like to thank the authors of that draft, Mark Cavage and Manu Sporny, for their work on that draft and their continuing contributions.

The editor would also like to thank the following individuals for feedback on and implementations of the draft-cavage-http-signatures draft (in alphabetical order):
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
James H. Manger,
Ilari Liusvaara,
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
Jeffrey Yasskin

# Document History
{:numbered="false"}

*RFC EDITOR: please remove this section before publication*

- draft-ietf-httpbis-message-signatures
  - Since -02
     * Clarified signing and verification processes.
     * Updated algorithm and key selection method.
     * Defined JOSE signature mapping process.
     * Removed legacy signature methods.

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
