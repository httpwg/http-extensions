# Document Shepherd Writeup

_This version is dated 8 April 2022._

Thank you for your service as a document shepherd. Among the responsibilities is answering the questions in this writeup to give helpful context to Last Call and Internet Engineering Steering Group (IESG) reviewers, and your diligence in completing it, is appreciated. The full role of the shepherd is further described in RFC 4858, and informally. You will need the cooperation of authors to complete these checks.

Note that some numbered items contain multiple related questions; please be sure to answer all of them.

## Document History

Answer either of the two options below (depending on the document type), then continue with the common part.

### Option 1: For Documents Coming from IETF Working Groups

Does the working group (WG) consensus represent the strong concurrence of a few individuals, with others being silent, or did it reach broad agreement?

Was there controversy about particular points, or were there decisions where the consensus was particularly rough?

### Option 2: For Individual Documents

Was the document considered in any WG, and if so, why was it not adopted as a work item there?
Was there controversy about particular points that caused the WG to not adopt the document?

## Common Part

Has anyone threatened an appeal or otherwise indicated extreme discontent? If so, please summarize the areas of conflict in separate email messages to the responsible Area Director. (It should be in a separate email because this questionnaire is publicly available.)

For protocol documents, are there existing implementations of the contents of the document? Have a significant number of potential implementers indicated plans to implement? Are any existing implementations reported somewhere, either in the document itself (as RFC 7942 recommends) or elsewhere (where)?

### Additional Reviews

Does this document need review from other IETF working groups or external organizations? Have those reviews occurred?

Describe how the document meets any required formal expert review criteria, such as the MIB Doctor, YANG Doctor, media type, and URI type reviews.

If the document contains a YANG module, has the final version of the module been checked with any of the [recommended validation tools](https://trac.ietf.org/trac/ops/wiki/yang-review-tools) for syntax and formatting validation? If there are any resulting errors or warnings, what is the justification for not fixing them at this time? Does the YANG module comply with the Network Management Datastore Architecture (NMDA) as specified in RFC 8342?

Describe reviews and automated checks performed to validate sections of the final version of the document written in a formal language, such as XML code, BNF rules, MIB definitions, CBOR's CDDL, etc.

### Document Shepherd Checks

Based on the shepherd's review of the document, is it their opinion that this document is needed, clearly written, complete, correctly designed, and ready to be handed off to the responsible Area Director?

Several IETF Areas have assembled [lists of common issues that their reviewers encounter](https://trac.ietf.org/trac/iesg/wiki/ExpertTopics). Do any such issues remain that would merit specific attention from subsequent reviews?

What type of RFC publication is being requested on the IETF stream (Best Current Practice, Proposed Standard, Internet Standard, Informational, Experimental, or Historic)? Why is this the proper type of RFC? Do all Datatracker state attributes correctly reflect this intent?

Has the interested community confirmed that any and all appropriate IPR disclosures required by BCP 78 and BCP 79 have been filed? If not, explain why. If yes, summarize any discussion and conclusion regarding the intellectual property rights (IPR) disclosures, including links to relevant emails.

Has each Author or Contributor confirmed their willingness to be listed as such? If the number of Authors/Editors on the front page is greater than 5, please provide a justification.

Identify any remaining I-D nits in this document. (See the [idnits tool](http://www.ietf.org/tools/idnits/) and the checkbox items found in Guidelines to Authors of Internet-Drafts). Simply running the idnits tool is not enough; please review the entire guidelines document.

Should any informative references be normative or vice-versa?

List any normative references that are not freely available to anyone. Did the community have sufficient access to review any such normative references?

Are there any normative downward references (see RFC 3967, BCP 97)? If so, list them.

Are there normative references to documents that are not ready for advancement or are otherwise in an unclear state? If they exist, what is the plan for their completion?

Will publication of this document change the status of any existing RFCs? If so, does the Datatracker metadata correctly reflect this and are those RFCs listed on the title page, in the abstract, and discussed in the introduction? If not, explain why and point to the part of the document where the relationship of this document to these other RFCs is discussed.

Describe the document shepherd's review of the IANA considerations section, especially with regard to its consistency with the body of the document. Confirm that all aspects of the document requiring IANA assignments are associated with the appropriate reservations in IANA registries. Confirm that any referenced IANA registries have been clearly identified. Confirm that each newly created IANA registry specifies its initial contents, allocations procedures, and a reasonable name (see RFC 8126).

List any new IANA registries that require Designated Expert Review for future allocations. Are the instructions to the Designated Expert clear? Please include suggestions of designated experts, if appropriate.
